# python3 test_compiler/sim_circuit.py results_diff_compiler/grid/qcnn/grid_optimal_8_0.csv grid qaoa

# time unit in this script is 1ns
SINGLE_QUBIT_GATE_DURATION = 25 #ns
TWO_QUBIT_GATE_DURATION = 10 #ns
MEASUREMENT_DURATION = 4000 #4us
T_1=15000
T_PHI=25000

MAX_NUM_LAYERS = 1500


def sim_circuit(phy_qubit_num, data, time_factor, single_qubit_gate_fid=None, two_qubit_gate_fid=None):
   
    # CZ means assuming native gate is C-phase like atom array
    # since we ignore the decoherence factor like atom array,
    # the duration of this hypothetical situation is not important
    if not two_qubit_gate_fid:
        if data["gateset"] == "CZ":
            two_qubit_gate_fid = 0.975
        # SYC means like original experiments
        if data["gateset"] == "SYC":
            two_qubit_gate_fid = 0.994
    if not single_qubit_gate_fid:
        if data["gateset"] == "CZ":
            single_qubit_gate_fid = 0.9999
        # SYC means like original experiments
        if data["gateset"] == "SYC":
            single_qubit_gate_fid = 0.999

    merge_gate(phy_qubit_num, data)
    qubit_last_layer, time_slot_matrix = scheduling(phy_qubit_num,data)
    new_calculate_qubit_idling_time(data, phy_qubit_num, qubit_last_layer, time_slot_matrix)
    data["g1"], data["g2"] = calculate_gate_number(data["gate_spec"])
    calculate_cir_fidelity(data, two_qubit_gate_fid, single_qubit_gate_fid, time_factor)

def calculate_gate_number(gate_spec):
    g1 = 0
    g2 = 0
    for g in gate_spec:
        if g == "sg":
            g1 += 1
        elif g == "tg":
            g2 += 1
    return (g1, g2)

def calculate_cir_fidelity(data, two_qubit_gate_fid, single_qubit_gate_fid, time_factor):
    fidelity = pow(single_qubit_gate_fid, data["g1"])
    fidelity *= pow(two_qubit_gate_fid, data["g2"])
    data["fidelity_no_decoherence"] = fidelity
    
    qubit_idling_list = data["qubit_idling_time"]
    for t in qubit_idling_list:
        fidelity *= (1 - ((1/3) * ( 1/(time_factor*T_1) + 1/(time_factor*T_PHI) ) * t))

    data['fidelity_no_crosstalk'] = fidelity

def new_calculate_qubit_idling_time(data, phy_qubit_num, qubit_last_time, time_slot_matrix):

    max_d =  max(qubit_last_time)
    gate_spec = data["gate_spec"]
    affective_q = []
    for q_id, q_last_time in enumerate(qubit_last_time):
        if q_last_time > 0:
            affective_q.append(q_id)
    qubit_idling_time = [0] * phy_qubit_num
    qubit_lifetime = [0] * phy_qubit_num

    for time in range(1,max_d):
        has_single_qubit_gate = False
        has_measurement = False
        for q in affective_q:
            if time_slot_matrix[q][time] == -1:
                continue
            gate_name = gate_spec[time_slot_matrix[q][time]]
            if gate_name == "sg":
                has_single_qubit_gate = True
            elif gate_name[0] == "m":
                has_measurement = True
                break
        for q in affective_q:
            if has_measurement:
                qubit_lifetime[q] += MEASUREMENT_DURATION
            elif has_single_qubit_gate: 
                qubit_lifetime[q] += SINGLE_QUBIT_GATE_DURATION
            else:
                qubit_lifetime[q] += TWO_QUBIT_GATE_DURATION
            
            if time_slot_matrix[q][time] == -1:
                if has_measurement:
                    qubit_idling_time[q] += MEASUREMENT_DURATION
                elif has_single_qubit_gate:
                    qubit_idling_time[q] += SINGLE_QUBIT_GATE_DURATION
                else:
                    qubit_idling_time[q] += TWO_QUBIT_GATE_DURATION
            else:
                gate_name = gate_spec[time_slot_matrix[q][time]]
                if gate_name == "sg":
                    if has_measurement:
                        qubit_idling_time[q] += (MEASUREMENT_DURATION-SINGLE_QUBIT_GATE_DURATION)
                elif gate_name == "tg":
                    if has_measurement:
                        qubit_idling_time[q] += (MEASUREMENT_DURATION-TWO_QUBIT_GATE_DURATION)
                    elif has_single_qubit_gate:
                        qubit_idling_time[q] += (SINGLE_QUBIT_GATE_DURATION-TWO_QUBIT_GATE_DURATION)

    data['D'] = max(qubit_lifetime)
    data['qubit_lifetime'] = list()
    data['qubit_idling_time'] = list()
    for lifetime, idling_time in zip (qubit_lifetime, qubit_idling_time):
        if lifetime > 0:
            data["qubit_idling_time"].append(idling_time)
            data["qubit_lifetime"].append(lifetime)

def scheduling(phy_qubit_num, data):
    gate_spec = data["gate_spec"]
    gate_pos = data["gates"]
    qubit_last_time = [0] * phy_qubit_num
    time_slot_matrix = [] 
    for _ in range(phy_qubit_num):
        time_slot_matrix.append([-1] * MAX_NUM_LAYERS )
    
    for g_id, (g, g_pos) in enumerate(zip(gate_spec, gate_pos)):
        if g == "sg":
            gate_start_time = qubit_last_time[g_pos[0]] + 1
            time_slot_matrix[g_pos[0]][gate_start_time] = g_id
            qubit_last_time[g_pos[0]] = gate_start_time
        elif g == "tg":
            gate_start_time = max(qubit_last_time[g_pos[0]], qubit_last_time[g_pos[1]]) + 1
            time_slot_matrix[g_pos[0]][gate_start_time] = g_id
            time_slot_matrix[g_pos[1]][gate_start_time] = g_id
            qubit_last_time[g_pos[0]] = gate_start_time
            qubit_last_time[g_pos[1]] = gate_start_time
        else:
            raise ValueError("invalid gate name\n")
    return (qubit_last_time, time_slot_matrix)

def merge_gate(phy_qubit_num, data):
    gate_spec = data["gate_spec"]
    gate_pos = data["gates"]
    new_gate_spec = []
    new_gate_pos = []
    q_last_gate_list = [""]*phy_qubit_num

    for g_slot, g_pos_slot in zip(gate_spec, gate_pos):
        for g, g_pos in zip(g_slot, g_pos_slot):
            if g == "ZZ":
                if data["gateset"] == "CZ":
                    # --.--Rz--
                    #   |   
                    # --.--Rz--
                    new_gate_spec.append("tg")
                    new_gate_pos.append(g_pos)
                    new_gate_spec.append("sg")
                    new_gate_pos.append([g_pos[0]])
                    new_gate_spec.append("sg")
                    new_gate_pos.append([g_pos[1]])
                    q_last_gate_list[g_pos[0]] = "sg"
                    q_last_gate_list[g_pos[1]] = "sg"
                else:
                    # --.--Rxz--.--Rxz--
                    #   |       |
                    # --.--Rxz--.--Rxz--
                    new_gate_spec.append("tg")
                    new_gate_pos.append(g_pos)
                    new_gate_spec.append("sg")
                    new_gate_pos.append([g_pos[0]])
                    new_gate_spec.append("sg")
                    new_gate_pos.append([g_pos[1]])
                    new_gate_spec.append("tg")
                    new_gate_pos.append(g_pos)
                    new_gate_spec.append("sg")
                    new_gate_pos.append([g_pos[0]])
                    new_gate_spec.append("sg")
                    new_gate_pos.append([g_pos[1]])
                    q_last_gate_list[g_pos[0]] = "sg"
                    q_last_gate_list[g_pos[1]] = "sg"
            elif g == "SWAP":
                # --.--Rxz--.--Rxz--.--Rxz--
                #   |       |       |
                # --.--Rxz--.--Rxz--.--Rxz--
                for _ in range(3):
                    new_gate_spec.append("tg")
                    new_gate_pos.append(g_pos)
                    new_gate_spec.append("sg")
                    new_gate_pos.append([g_pos[0]])
                    new_gate_spec.append("sg")
                    new_gate_pos.append([g_pos[1]])
                q_last_gate_list[g_pos[0]] = "sg"
                q_last_gate_list[g_pos[1]] = "sg"
            else:
                raise ValueError("invalid gate name\n")
    assert(len(new_gate_spec) == len(new_gate_pos))
    data["gate_spec"] = new_gate_spec
    data["gates"] = new_gate_pos


    
    
