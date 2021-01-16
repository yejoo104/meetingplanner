from algorithms import modify_slots

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
    
    assert modify_slots(30, slot_dict, dates, 15, 19) == slot_dict
    assert modify_slots(60, slot_dict, dates, 15, 19) == {"202012311500": [],
                  "202012311530": [],
                  "202012311600": ["A"],
                  "202012311630": ["A", "B"],
                  "202012311700": ["A", "C", "D"],
                  "202012311730": ["C"],
                  "202012311800": ["B"],
                  "202101011500": ["A", "B", "C", "D", "E"],
                  "202101011530": ["A", "C", "D", "E"],
                  "202101011600": ["C", "D", "E", "F"],
                  "202101011630": ["D", "E", "F"],
                  "202101011700": [],
                  "202101011730": [],
                  "202101011800": [],
                  "202101021500": [],
                  "202101021530": [],
                  "202101021600": ["E", "H"],
                  "202101021630": ["H"],
                  "202101021700": [],
                  "202101021730": ["A"],
                  "202101021800": ["A", "C"]}

test_modify_slots()
