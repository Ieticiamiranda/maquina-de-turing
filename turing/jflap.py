#!/usr/bin/env python3
"""
utilitário de linha de comando para gerar e salvar arquivo .jff
nomeia o arquivo combinando o nome da operação e a data/hora atual
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
import math
import sys
from datetime import datetime

# adiciona o diretório de trabalho para importar as máquinas definidas
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CURRENT_DIR)
from turing import TMFactory

def generate_jff_single_tape(name, states_list, initial_state, final_states, transitions_dict, filepath):
    """
    constrói o arquivo xml no formato nativo do jflap
    organiza os estados em disposição circular para melhor legibilidade visual
    """
    root = ET.Element("structure")
    type_el = ET.SubElement(root, "type")
    type_el.text = "turing"
    
    automaton = ET.SubElement(root, "automaton")
    state_to_id = {}
    
    n = len(states_list)
    radius = max(180, n * 35)
    cx, cy = radius + 80, radius + 80
    
    for idx, st in enumerate(states_list):
        state_to_id[st] = idx
        angle = 2 * math.pi * idx / n
        x = int(cx + radius * math.cos(angle))
        y = int(cy + radius * math.sin(angle))
        
        st_el = ET.SubElement(automaton, "state", id=str(idx), name=st)
        x_el = ET.SubElement(st_el, "x")
        x_el.text = f"{x}.0"
        y_el = ET.SubElement(st_el, "y")
        y_el.text = f"{y}.0"
        
        if st == initial_state:
            ET.SubElement(st_el, "initial")
        if st in final_states:
            ET.SubElement(st_el, "final")

    for (from_st, read_sym), trans in transitions_dict.items():
        if from_st not in state_to_id or trans.new_state not in state_to_id:
            continue
            
        trans_el = ET.SubElement(automaton, "transition")
        
        from_el = ET.SubElement(trans_el, "from")
        from_el.text = str(state_to_id[from_st])
        
        to_el = ET.SubElement(trans_el, "to")
        to_el.text = str(state_to_id[trans.new_state])
        
        read_el = ET.SubElement(trans_el, "read")
        read_el.text = "" if read_sym == "_" else read_sym
        
        write_el = ET.SubElement(trans_el, "write")
        write_el.text = "" if trans.write_symbol == "_" else trans.write_symbol
        
        move_el = ET.SubElement(trans_el, "move")
        move_el.text = trans.direction

    xml_str = ET.tostring(root, encoding="utf-8")
    parsed = minidom.parseString(xml_str)
    pretty_xml = parsed.toprettyxml(indent="  ")
    cleaned_xml = "\n".join([line for line in pretty_xml.split("\n") if line.strip()])
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(cleaned_xml)
    print(f"arquivo jflap salvo: {filepath}")

def save_operation_jff(choice="1"):
    # cria a pasta de saída para os arquivos .jff
    out_dir = os.path.join(CURRENT_DIR, "jflap")
    os.makedirs(out_dir, exist_ok=True)

    # formato da hora de salvamento: DIA_MES_HORA-MIN
    timestamp = datetime.now().strftime("%d_%m_%H-%M")

    from dataclasses import dataclass
    @dataclass
    class Trans:
        new_state: str
        write_symbol: str
        direction: str

    if choice == "1":
        op_name = "incremento_binario"
        m = TMFactory.binary_increment()
        states = ["q0", "q1", "qf"]
        t = m.transitions
    elif choice == "2":
        op_name = "adicao_unaria"
        m = TMFactory.unary_addition()
        states = ["q0", "q1", "q2", "qf"]
        t = m.transitions
    elif choice == "3":
        op_name = "copia_string"
        m = TMFactory.binary_copy()
        states = ["q0", "qA", "qB", "qAI", "qBI", "qA1", "qB1", "qRet", "qFixL", "qFix", "qf"]
        t = m.transitions
    elif choice == "4":
        op_name = "complemento_de_dois"
        m = TMFactory.twos_complement()
        states = ["q0", "q1", "q2", "qf"]
        t = m.transitions
    elif choice == "5":
        op_name = "adicao_binaria"
        states = ["q0", "qDecB", "qGoToA", "qIncA", "qBackToB", "qClean", "qf"]
        t = {
            ("q0", "0"): Trans("q0", "0", "R"),
            ("q0", "1"): Trans("q0", "1", "R"),
            ("q0", "+"): Trans("q0", "+", "R"),
            ("q0", "_"): Trans("qDecB", "_", "L"),
            ("qDecB", "0"): Trans("qDecB", "1", "L"),
            ("qDecB", "1"): Trans("qGoToA", "0", "L"),
            ("qDecB", "+"): Trans("qClean", "_", "R"),
            ("qGoToA", "0"): Trans("qGoToA", "0", "L"),
            ("qGoToA", "1"): Trans("qGoToA", "1", "L"),
            ("qGoToA", "+"): Trans("qIncA", "+", "L"),
            ("qIncA", "1"): Trans("qIncA", "0", "L"),
            ("qIncA", "0"): Trans("qBackToB", "1", "R"),
            ("qIncA", "_"): Trans("qBackToB", "1", "R"),
            ("qBackToB", "0"): Trans("qBackToB", "0", "R"),
            ("qBackToB", "1"): Trans("qBackToB", "1", "R"),
            ("qBackToB", "+"): Trans("qBackToB", "+", "R"),
            ("qBackToB", "_"): Trans("qDecB", "_", "L"),
            ("qClean", "0"): Trans("qClean", "_", "R"),
            ("qClean", "1"): Trans("qClean", "_", "R"),
            ("qClean", "_"): Trans("qf", "_", "L"),
        }
    else:
        print("opção inválida.")
        return

    filename = f"{op_name}_{timestamp}.jff"
    filepath = os.path.join(out_dir, filename)
    generate_jff_single_tape(op_name, states, "q0", {"qf"}, t, filepath)

def main():
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        print("qual operação deseja salvar em jff?")
        print("1. incremento binário")
        print("2. adição unária")
        print("3. cópia de string")
        print("4. complemento de dois")
        print("5. adição binária")
        choice = input("escolha (1-5): ").strip()
    save_operation_jff(choice)

if __name__ == "__main__":
    main()
