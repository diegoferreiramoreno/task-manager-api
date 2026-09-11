from datetime import datetime, timedelta, time, date
from typing import List, Protocol, Set, Dict
import pytz
import requests
import models

TZ_BR = pytz.timezone("America/Sao_Paulo")

class HolidayProviderInterface(Protocol):
    def is_holiday(self, date_obj: datetime) -> bool:
        ...

class BrasilApiHolidayProvider:
    def __init__(self):
        # Cache simples em memória: { 2023: {date1, date2, ...}, 2024: {...} }
        self._cache: Dict[int, Set[date]] = {}
        # URL base da BrasilAPI
        self.BASE_URL = "https://brasilapi.com.br/api/feriados/v1/"

    def _fetch_holidays(self, year: int) -> Set[date]:
        """"
        Vai na API externa, busca os feriados do ano e armazena no cache.
        """
        if year in self._cache:
            return self._cache[year]

        response = requests.get(f"{self.BASE_URL}{year}")
        response.raise_for_status()
        holidays_data = response.json()

        holidays_set = set()
        for holiday in holidays_data:
            holiday_date = datetime.strptime(holiday["date"], "%Y-%m-%d").date()
            holidays_set.add(holiday_date)

        self._cache[year] = holidays_set
        return holidays_set
    
    def is_holiday(self, date_obj: datetime) -> bool:
        """
        Verifica se a data é feriado consultando o cache ou a API.
        """
        year = date_obj.year
        holidays = self._fetch_holidays(year)
        return date_obj.date() in holidays

class HolidayFromDBProviderInterface(Protocol):
    def is_holiday(self, date_obj: datetime) -> bool:
        ...    
class HolidayFromDBProvider:
    def __init__(self, db_session):
        self.db_session = db_session

    def is_holiday(self, date_obj: datetime) -> bool:
        """
        Verifica se a data é feriado consultando o banco de dados local.
        """
        query_dt = date_obj
        if date_obj.tzinfo is not None:
            query_dt = date_obj.replace(tzinfo=None)
        holiday = self.db_session.query(models.Holiday).filter(
            models.Holiday.start_date <= query_dt,
            (models.Holiday.end_date == None) | (models.Holiday.end_date >= query_dt)
        ).first()
        return holiday is not None

class GapAnalyzer:
    def __init__(self, holiday_provider: HolidayProviderInterface, holiday_db_provider: HolidayFromDBProviderInterface):
        self.holiday_provider = holiday_provider
        self.holiday_db_provider = holiday_db_provider
        # Configuração Hardcoded (em prod poderia vir de um config/env)
        self.WORK_START = time(8, 0)  # 08:00
        self.WORK_END = time(17, 0)   # 17:00

    def _is_working_day(self, date_obj: datetime) -> bool:
        """Checks if it is Mon-Fri and not a holiday."""
        if date_obj.weekday() >= 5: # 5=Sat, 6=Sun
            return False
        
        if self.holiday_provider.is_holiday(date_obj):
            return False
        if self.holiday_db_provider.is_holiday(date_obj):
            return False
                        
        return True

    def calculate_gaps(self, query_start: datetime, query_end: datetime, tasks: List[models.Task]) -> List[dict]:
        gaps = []
        
        # O cursor começa no início da query
        current_cursor = query_start

        # Ordenar tarefas por data de início
        sorted_tasks = sorted(tasks, key=lambda t: t.start_date)

        for task in sorted_tasks:
            # Se a tarefa termina antes do nosso cursor, ignora (já passou)
            if task.end_date < current_cursor:
                continue

            # Se a tarefa começa depois do cursor, temos um potencial buraco
            if task.start_date > current_cursor:
                # O buraco cru é do cursor até o início da tarefa
                raw_gap_start = current_cursor
                raw_gap_end = task.start_date
                
                # Processa esse intervalo aplicando regra 08:00-17:00 e dias úteis
                clean_gaps = self._process_business_hours_gap(raw_gap_start, raw_gap_end)
                gaps.extend(clean_gaps)

            # Avança o cursor para o final da tarefa atual
            if task.end_date > current_cursor:
                current_cursor = task.end_date

        # Checa o espaço final entre a última tarefa e o fim da query
        if current_cursor < query_end:
            clean_gaps = self._process_business_hours_gap(current_cursor, query_end)
            gaps.extend(clean_gaps)

        return gaps

    def _process_business_hours_gap(self, start_dt: datetime, end_dt: datetime) -> List[dict]:
        """
        Slices a raw gap (e.g. 2 days long) into specific business hour slots (08-17).
        """
        valid_segments = []
        
        # Vamos iterar dia a dia, começando do dia do início do gap
        current_day_iterator = start_dt.date()
        target_end_date = end_dt.date()

        while current_day_iterator <= target_end_date:
            
            check_date = datetime.combine(current_day_iterator, time(12,0))
            check_date = TZ_BR.localize(check_date)
            # 1. Se não for dia útil, pula para o próximo dia
            if not self._is_working_day(check_date):
                current_day_iterator += timedelta(days=1)
                continue

            # 2. Define os limites de trabalho para AQUELE dia específico
            # Ex: Dia 10/01 08:00 até Dia 10/01 17:00
            naive_start = datetime.combine(current_day_iterator, self.WORK_START)
            naive_end = datetime.combine(current_day_iterator, self.WORK_END)
            day_work_start = TZ_BR.localize(naive_start)
            day_work_end = TZ_BR.localize(naive_end)

            # 3. Cálculo de Interseção (O Pulo do Gato)
            # O início efetivo é o MAIOR entre: O início do gap e o início do expediente
            effective_start = max(start_dt, day_work_start)
            
            # O fim efetivo é o MENOR entre: O fim do gap e o fim do expediente
            effective_end = min(end_dt, day_work_end)

            # 4. Se o início for menor que o fim, temos um gap válido neste dia
            if effective_start < effective_end:
                duration = (effective_end - effective_start).total_seconds() / 3600
                
                if duration > 0.01: # Filtrar microssegundos irrelevantes
                    valid_segments.append({
                        "start_date": effective_start,
                        "end_date": effective_end,
                        "duration_hours": round(duration, 2),
                        "message": "Available slot (Business Hours)"
                    })

            # Avança para o próximo dia
            current_day_iterator += timedelta(days=1)

        return valid_segments