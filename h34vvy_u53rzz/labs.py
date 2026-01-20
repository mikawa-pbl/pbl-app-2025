from dataclasses import dataclass


@dataclass
class Lab:
    id: str
    name: str
    department: str


LABORATORIES = [
    # 1系 (Mechanical Engineering)
    Lab("lab_micro_nano", "マイクロ・ナノ機械システム研究室", "1"),
    Lab("lab_high_throughput", "ハイスループットマイクロ・ナノ工学研究室", "1"),
    Lab("lab_mech_dynamics", "機械ダイナミクス研究室", "1"),
    Lab("lab_func_mat_struct", "機能材料・構造システム研究室", "1"),
    Lab("lab_mat_func_ctrl", "材料機能制御研究室", "1"),
    Lab("lab_high_strength", "高強度マテリアル開発評価研究室", "1"),
    Lab("lab_mat_assurance", "材料保証研究室", "1"),
    Lab("lab_robotics_mecha", "ロボティクス・メカトロニクス研究室", "1"),
    Lab("lab_measure_sys", "計測システム研究室", "1"),
    Lab("lab_sys_eng", "システム工学研究室", "1"),
    Lab("lab_intel_mat", "知能材料ロボティクス研究室", "1"),
    Lab("lab_env_energy", "環境エネルギー変換工学研究室", "1"),
    Lab("lab_thermo_fluid", "環境熱流体工学研究室", "1"),
    Lab("lab_natural_energy", "自然エネルギー変換科学研究室", "1"),
    Lab("lab_energy_saving", "省エネルギー工学研究室", "1"),

    # 2系 (Electrical & Electronic Info Eng)
    Lab("lab_func_mat_sci", "機能性材料科学研究室", "2"),
    Lab("lab_spin_elec", "スピンエレクトロニクスグループ", "2"),
    Lab("lab_nano_quantum", "ナノ量子オプトエレクトロニクスグループ", "2"),
    Lab("lab_process_eval", "プロセス・評価解析研究室", "2"),
    Lab("lab_optical_meas", "光計測化学研究室", "2"),
    Lab("lab_clean_energy_dev", "クリーンエネルギーデバイス研究室", "2"),
    Lab("lab_clean_energy_sys", "クリーンエネルギーシステム研究室", "2"),
    Lab("lab_plasma_energy", "プラズマエネルギーシステム研究室", "2"),
    Lab("lab_dielectric", "誘電・絶縁システム研究室", "2"),
    Lab("lab_high_volt", "高電圧応用・計測研究室", "2"),
    Lab("lab_bio_sensor_1", "集積化バイオセンサ・MEMSグループ【Ⅰ】", "2"),
    Lab("lab_bio_sensor_2", "集積化バイオセンサ・MEMSグループ【Ⅱ】", "2"),
    Lab("lab_integrated_optic", "集積光デバイスグループ", "2"),
    Lab("lab_integrated_circuit", "集積回路・センサシステムグループ", "2"),
    Lab("lab_applied_phys", "応用物性プロセス研究室", "2"),
    Lab("lab_bio_sensor_3", "集積化バイオセンサ・MEMSグループ【Ⅲ】", "2"),
    Lab("lab_dedicated_calc", "専用計算システム研究室", "2"),
    Lab("lab_wireless_comm", "ワイヤレス通信研究室", "2"),
    Lab("lab_electromagnetic", "電磁波工学研究室", "2"),
    Lab("lab_comm_signal", "通信信号処理研究室", "2"),
    Lab("lab_smart_sys", "スマートシステム研究室", "2"),
    Lab("lab_applied_mag", "応用電磁気研究室", "2"),

    # 3系 (CS/Info/Intelligence)
    Lab("lab_info_net", "情報ネットワーク研究室", "3"),
    Lab("lab_info_sec", "情報セキュリティ研究室", "3"),
    Lab("lab_quantum_bio", "量子生物学研究室", "3"),
    Lab("lab_comp_sys_perf", "計算機システム性能工学研究室", "3"),
    Lab("lab_quantum_info", "量子情報研究室", "3"),
    Lab("lab_comp_chem", "計算化学研究室", "3"),
    Lab("lab_dist_sys", "分散システム研究室", "3"),
    Lab("lab_spoken_lang", "音声言語処理研究室", "3"),
    Lab("lab_app_info", "応用情報システム研究室", "3"),
    Lab("lab_nlp", "自然言語処理研究室", "3"),
    Lab("lab_learning_inf", "学習推論システム研究室", "3"),
    Lab("lab_speech_intel", "音声知能システム研究室", "3"),
    Lab("lab_visual_psych", "視覚心理物理学研究室", "3"),
    Lab("lab_visual_percept", "視覚認知情報学研究室", "3"),
    Lab("lab_cognitive_neuro", "認知神経工学研究室", "3"),
    Lab("lab_neural_info", "脳神経情報動態研究室", "3"),
    Lab("lab_bio_motor", "生体運動制御システム研究室", "3"),
    Lab("lab_comp_intel", "計算知能研究室", "3"),
    Lab("lab_auditory", "聴覚心理物理学研究室", "3"),
    Lab("lab_visual_neuro", "視覚神経科学研究室", "3"),
    Lab("lab_interaction", "インタラクションデザイン研究室", "3"),
    Lab("lab_graphic_media", "グラフィックメディア研究室", "3"),

    # 4系 (Applied Chem/Life Sci)
    Lab("lab_func_interface", "機能性界面科学研究室", "4"),
    Lab("lab_micro_sep", "マイクロ分離科学研究室", "4"),
    Lab("lab_func_polymer", "機能性高分子化学研究室", "4"),
    Lab("lab_env_mat", "環境材料工学研究室", "4"),
    Lab("lab_func_catalyst", "機能触媒システム工学研究室", "4"),
    Lab("lab_reaction_eng", "反応エネルギー工学研究室", "4"),
    Lab("lab_polymer_mat", "高分子材料工学研究室", "4"),
    Lab("lab_mol_genetics", "分子遺伝学研究室", "4"),
    Lab("lab_reactive_plasma", "反応性プラズマ科学研究室", "4"),
    Lab("lab_interface_phys", "界面物理化学研究室", "4"),
    Lab("lab_mol_cell_bio", "分子細胞生物工学研究室", "4"),
    Lab("lab_genetic_eng", "遺伝子工学研究室", "4"),
    Lab("lab_genome_photo", "ゲノム光生物学研究室", "4"),
    Lab("lab_org_reaction", "有機反応化学研究室", "4"),
    Lab("lab_reg_biofunc", "生態機能制御工学研究室", "4"),
    Lab("lab_app_symbiosis", "応用共生学研究室", "4"),
    Lab("lab_resource_circ", "資源循環工学研究室", "4"),
    Lab("lab_phys_bio", "生命機能科学研究室", "4"),

    # 5系 (Architecture/Civil Eng) - To be added
]
