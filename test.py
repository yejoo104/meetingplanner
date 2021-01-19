from algorithms import next_slot, modify_slots, remove_unavailable_slots

def test_next_slot():
    assert next_slot("20201231800830") == "20201231830900"
    assert next_slot("20201231330400") == "20201231400430"
    assert next_slot("2021010117001730") == "2021010117301800"
    assert next_slot("2021010119302000") == "2021010120002030"
    assert next_slot("202010319301000") == "2020103110001030"

def test_modify_slots():
    dates = ["20201231", "20210101", "20210102"]
    slot_dict = {"2020123115001530": [],
                  "2020123115301600": [],
                  "2020123116001630": ["A"],
                  "2020123116301700": ["A", "B"],
                  "2020123117001730": ["A", "B", "C", "D"],
                  "2020123117301800": ["A", "C", "D"],
                  "2020123118001830": ["B", "C"],
                  "2020123118301900": ["B", "D"],
                  "2021010115001530": ["A", "B", "C", "D", "E", "F"],
                  "2021010115301600": ["A", "B", "C", "D", "E"],
                  "2021010116001630": ["A", "C", "D", "E", "F", "G"],
                  "2021010116301700": ["B", "C", "D", "E", "F", "H"],
                  "2021010117001730": ["A", "D", "E", "F"],
                  "2021010117301800": [],
                  "2021010118001830": ["E", "F"],
                  "2021010118301900": ["H"],
                  "2021010215001530": ["B", "C", "G"],
                  "2021010215301600": ["A", "D"],
                  "2021010216001630": ["E", "F", "H"],
                  "2021010216301700": ["E", "H"],
                  "2021010217001730": ["H"],
                  "2021010217301800": ["A"],
                  "2021010218001830": ["A", "C"],
                  "2021010218301900": ["A", "C"]}
    slot_dict_sets = {key[:8 + (len(key) - 8) // 2]: set(value) for key, value in slot_dict.items()}
    
    assert modify_slots(30, slot_dict, dates, 15, 19) == slot_dict_sets
    assert modify_slots(60, slot_dict, dates, 15, 19) == {"202012311500": set(),
                  "202012311530": set(),
                  "202012311600": {"A"},
                  "202012311630": {"A", "B"},
                  "202012311700": {"A", "C", "D"},
                  "202012311730": {"C"},
                  "202012311800": {"B"},
                  "202012311830": set(),
                  "202101011500": {"A", "B", "C", "D", "E"},
                  "202101011530": {"A", "C", "D", "E"},
                  "202101011600": {"C", "D", "E", "F"},
                  "202101011630": {"D", "E", "F"},
                  "202101011700": set(),
                  "202101011730": set(),
                  "202101011800": set(),
                  "202101011830": set(),
                  "202101021500": set(),
                  "202101021530": set(),
                  "202101021600": {"E", "H"},
                  "202101021630": {"H"},
                  "202101021700": set(),
                  "202101021730": {"A"},
                  "202101021800": {"A", "C"},
                  "202101021830": set()}
    assert modify_slots(90, slot_dict, dates, 15, 19) == {"202012311500": set(),
                  "202012311530": set(),
                  "202012311600": {"A"},
                  "202012311630": {"A"},
                  "202012311700": {"C"},
                  "202012311730": set(),
                  "202012311800": set(),
                  "202012311830": set(),
                  "202101011500": {"A", "C", "D", "E"},
                  "202101011530": {"C", "D", "E"},
                  "202101011600": {"D", "E", "F"},
                  "202101011630": set(),
                  "202101011700": set(),
                  "202101011730": set(),
                  "202101011800": set(),
                  "202101011830": set(),
                  "202101021500": set(),
                  "202101021530": set(),
                  "202101021600": {"H"},
                  "202101021630": set(),
                  "202101021700": set(),
                  "202101021730": {"A"},
                  "202101021800": set(),
                  "202101021830": set()}
    assert modify_slots(120, slot_dict, dates, 15, 19) == {"202012311500": set(),
                  "202012311530": set(),
                  "202012311600": {"A"},
                  "202012311630": set(),
                  "202012311700": set(),
                  "202012311730": set(),
                  "202012311800": set(),
                  "202012311830": set(),
                  "202101011500": {"C", "D", "E"},
                  "202101011530": {"D", "E"},
                  "202101011600": set(),
                  "202101011630": set(),
                  "202101011700": set(),
                  "202101011730": set(),
                  "202101011800": set(),
                  "202101011830": set(),
                  "202101021500": set(),
                  "202101021530": set(),
                  "202101021600": set(),
                  "202101021630": set(),
                  "202101021700": set(),
                  "202101021730": set(),
                  "202101021800": set(),
                  "202101021830": set()}

def test_remove_unavailable_slots():
    slot1 = {"202008231500": set(), "202008231530": {"yej"}, "202008231600": {"bleh", "yej"}}
    assert remove_unavailable_slots(slot1) == ({"202008231530": {"yej"}, "202008231600": {"bleh", "yej"}}, ["yej", "bleh"])
    slot2 = {"20210101300": set(), "20210101400": set(), "20210101500": set()}
    assert remove_unavailable_slots(slot2) == ({}, [])

test_next_slot()
test_modify_slots()
test_remove_unavailable_slots()
