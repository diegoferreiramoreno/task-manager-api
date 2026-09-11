import sys

# Em 1991 não tinhamos "dataclasses" ou "pydantic".
# Usamos dicionairios ou tuplas.
TASKS_DB = [
    {"code": "TSK-01", "start": 8,  "end": 10, "name": "Analise"},
    {"code": "TSK-02", "start": 10, "end": 12, "name": "Codificacao"},
    # GAP das 12 as 13 (almoco estendido?)
    {"code": "TSK-03", "start": 13, "end": 16, "name": "Testes Unitarios"},
    # GAP das 16 as 17 (café da tarde demorado)
]

def render_ascii_dashboard():
    print "============================================================"
    print " SISTEMA DE CONTROLE DE TAREFAS (v0.9 BETA) - 1991"
    print "============================================================"
    print ""
    print "VISUALIZACAO DE GAPS (Dia: 02/01/1991)"
    print "Escala: Cada '#' = 30 minutos de trabalho"
    print "        Cada '.' = 30 minutos de ociosidade (GAP)"
    print ""
    print "HORA  | VISUALIZACAO                     | STATUS"
    print "------+----------------------------------+------------------"

    # O dia de trabalho vai das 8h as 18h
    start_hour = 8
    end_hour = 18
    
    current_time = start_hour
    
    while current_time < end_hour:
        # Logica "Procedural" pura (sem LINQ ou lambdas sofisticados)
        status = "GAP (Ocioso)"
        bar_char = ".." # O padrao eh gap
        task_name = ""
        
        # Procura se tem tarefa nessa hora (Linear Search, sem index)
        for task in TASKS_DB:
            if current_time >= task["start"] and current_time < task["end"]:
                status = task["code"]
                bar_char = "##"
                task_name = task["name"]
                break
        
        # Construcao da linha do relatorio
        # %02d = Inteiro com 2 digitos (ex: 08, 09)
        # %s = String
        time_label = "%02d:00" % current_time
        
        # A barra grafica eh feita repetindo o caractere
        # Simulando uma barra de progresso visual
        visual_bar = bar_char * 10 
        
        if status != "GAP (Ocioso)":
            desc = "%s - %s" % (status, task_name)
        else:
            desc = ">>> ATENCAO: OCIOSIDADE <<<"
            
        print "%s | %s | %s" % (time_label, visual_bar, desc)
        
        # Avanca 1 hora
        current_time = current_time + 1

    print "------+----------------------------------+------------------"
    print "FIM DO RELATORIO."

if __name__ == "__main__":
    render_ascii_dashboard()