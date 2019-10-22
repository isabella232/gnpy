J = {
    "elements": [],
    "connections": [],
}

def unidir_join(a, b):
    global J
    J["connections"].append(
        {"from_node": a, "to_node": b}
    )

def mk_edfa(name, gain, voa=0.0):
    global J
    J["elements"].append(
        {"uid": name, "type": "Edfa", "type_variety": f"fixed{gain}", "operational": {"gain_target": gain, "out_voa": voa}}
    )

def add_att(a, b, att):
    global J
    uid = f"att-{a}-{b}"
    J["elements"].append(
        {"uid": uid, "type": "Fused", "params": {"loss": att}},
    )
    unidir_join(a, uid)
    unidir_join(uid, b)
    return uid


AMS = 'Amsterdam'
BRE = 'Bremen'
COL = 'Cologne'

def build_fiber(city1, city2):
    global J
    J["elements"].append(
        {
            "uid": f"fiber-{city1}-{city2}",
            "type": "Fiber",
            "type_variety": "SSMF",
            "params": {
                "length": 50,
                "length_units": "km",
                "loss_coef": 0.2,
                "con_in": 1.5,
                "con_out": 1.5,
            }
        }
    )

for CITY in (AMS, BRE, COL):
    J["elements"].append(
        {"uid": f"roadm-{CITY}", "type": "Roadm", "params": {"target_pch_out_db": -12.5}}
    )
    # transceivers
    J["elements"].append(
        {"uid": f"trx-{CITY}", "type": "Transceiver"}
    )
    mk_edfa(f"roadm-{CITY}-AD-add", 22, 22)
    mk_edfa(f"roadm-{CITY}-AD-drop", 27, 10)
    add_att(f"trx-{CITY}", f"roadm-{CITY}-AD-add", 19.9)
    add_att(f"roadm-{CITY}-AD-drop", f"trx-{CITY}", 0)
    #J["elements"].append(
    #    {"uid": f"att-trx-{CITY}", "type": "Fused", "params": {"loss": 22}},
    #)
    #unidir_join(f"trx-{CITY}", f"att-trx-{CITY}")
    #unidir_join(f"att-trx-{CITY}", f"roadm-{CITY}-AD-add")
    #unidir_join(f"roadm-{CITY}-AD-drop", f"att-trx-{CITY}")
    #unidir_join(f"att-trx-{CITY}", f"trx-{CITY}")
    for n in (1,2):
        mk_edfa(f"roadm-{CITY}-L{n}-booster", 22)
        mk_edfa(f"roadm-{CITY}-L{n}-preamp", 27)
        #unidir_join(f"roadm-{CITY}-AD-add", f"roadm-{CITY}-L{n}-booster")
        unidir_join(f"roadm-{CITY}-AD-add", f"roadm-{CITY}")
        unidir_join(f"roadm-{CITY}", f"roadm-{CITY}-L{n}-booster")
        #add_att(f"roadm-{CITY}-L{n}-preamp", f"roadm-{CITY}-AD-drop", 27)
        unidir_join(f"roadm-{CITY}-L{n}-preamp", f"roadm-{CITY}")
        add_att(f"roadm-{CITY}", f"roadm-{CITY}-AD-drop", 0)
        for m in (1,2):
            if m == n:
                continue
            #add_att(f"roadm-{CITY}-L{n}-preamp", f"roadm-{CITY}-L{m}-booster", 22)
            unidir_join(f"roadm-{CITY}-L{n}-preamp", f"roadm-{CITY}")
            unidir_join(f"roadm-{CITY}", f"roadm-{CITY}-L{m}-booster")

#for LONG in ((AMS, BRE), (BRE, AMS)):
#for LONG in ((AMS, BRE),):
#for LONG in ((AMS, BRE), (BRE, COL)):
for LONG in ((AMS, BRE), (BRE, COL), (COL, AMS)):
    city1, city2 = LONG
    build_fiber(city1, city2)
    unidir_join(f"roadm-{city1}-L1-booster", f"fiber-{city1}-{city2}")
    unidir_join(f"fiber-{city1}-{city2}", f"roadm-{city2}-L2-preamp")
    build_fiber(city2, city1)
    unidir_join(f"roadm-{city2}-L2-booster", f"fiber-{city2}-{city1}")
    unidir_join(f"fiber-{city2}-{city1}", f"roadm-{city2}-L1-preamp")


#unidir_join("roadm-Amsterdam-L1-booster", "fiber-Amsterdam-Bremen")
#unidir_join("fiber-Amsterdam-Bremen", "roadm-Bremen-L1-preamp")
#unidir_join("roadm-Bremen-L1-booster", "fiber-Amsterdam-Bremen")
#unidir_join("fiber-Amsterdam-Bremen", "roadm-Amsterdam-L1-preamp")
#
#unidir_join("roadm-Bremen-L2-booster", "fiber-Bremen-Cologne")
#unidir_join("fiber-Bremen-Cologne", "roadm-Cologne-L2-preamp")
#unidir_join("roadm-Cologne-L2-booster", "fiber-Bremen-Cologne")
#unidir_join("fiber-Bremen-Cologne", "roadm-Bremen-L2-preamp")
#
#unidir_join("roadm-Cologne-L1-booster", "fiber-Cologne-Amsterdam")
#unidir_join("fiber-Cologne-Amsterdam", "roadm-Amsterdam-L2-preamp")
#unidir_join("roadm-Amsterdam-L2-booster", "fiber-Cologne-Amsterdam")
#unidir_join("fiber-Cologne-Amsterdam", "roadm-Cologne-L1-preamp")

for _, E in enumerate(J["elements"]):
    uid = E["uid"]
    if uid.startswith("roadm-") and (uid.endswith("-L1-booster") or uid.endswith("-L2-booster")):
        E["operational"]["out_voa"] = 12.5
    #if uid.endswith("-AD-add"):
    #    E["operational"]["out_voa"] = 21

import json
print(json.dumps(J, indent=2))
