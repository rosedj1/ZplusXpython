from Utils_ROOT.ROOT_classes import make_TH2F

h2_n3p1fcombos_n2p2fcombos = make_TH2F(
    "h2_n3p1fcombos_n2p2fcombos",
    title="",
    n_binsx=12, x_label=r"Number of 2P2F Lepton Quartets per Event",
    x_units=None, x_min=0, x_max=12,
    n_binsy=6, y_label=r"Number of 3P1F Lepton Quartets per Event",
    y_units=None, y_min=0, y_max=6,
    z_min=0, z_max=10000, z_label_size=None,
    n_contour=100)

h2_ntightleps_vs_ntotleps = make_TH2F(
    "h2_ntightleps_vs_ntotleps",
    title=None,
    n_binsx=10, x_label=r"Number of leptons per event",
    x_units=None, x_min=2, x_max=12,
    n_binsy=8, y_label=r"Number of tight leptons per event",
    y_units=None, y_min=0, y_max=8,
    z_min=0, z_max=5.5E6, z_label_size=None,
    n_contour=100)

h2_nlooseleps_vs_ntotleps = make_TH2F(
    "h2_nlooseleps_vs_ntotleps",
    title=None,
    n_binsx=10, x_label=r"Number of leptons per event",
    x_units=None, x_min=2, x_max=12,
    n_binsy=8, y_label=r"Number of loose leptons per event",
    y_units=None, y_min=0, y_max=8,
    z_min=0, z_max=5.5E6, z_label_size=None,
    n_contour=100)

h2_nlooseleps_vs_ntightleps_evtsel_cjlst = make_TH2F(
    "h2_nlooseleps_vs_ntightleps_evtsel_cjlst",
    title="Old Correct Event Selection (CJLST)",
    n_binsx=7, x_label=r"Number of tight leptons per event",
    x_units=None, x_min=2, x_max=9,
    n_binsy=10, y_label=r"Number of loose leptons per event",
    y_units=None, y_min=1, y_max=11,
    z_min=0, z_max=5.5E6, z_label_size=None,
    n_contour=100)

h2_nlooseleps_vs_ntightleps_reallyrelaxed = make_TH2F(
    "h2_nlooseleps_vs_ntightleps_reallyrelaxed",
    title="Really Relaxed Event Selection",
    n_binsx=3, x_label=r"Number of tight leptons per event",
    x_units=None, x_min=2, x_max=5,
    n_binsy=3, y_label=r"Number of loose leptons per event",
    y_units=None, y_min=0, y_max=3,
    z_min=0, z_max=5.5E6, z_label_size=None,
    n_contour=100)

h2_nlooseleps_vs_ntightleps_evtsel_cjlst_badsmartcut = make_TH2F(
    "h2_nlooseleps_vs_ntightleps_evtsel_cjlst_badsmartcut",
    title="Old Correct Event Selection (CJLST, no m_{Z_b} < 12 GeV)",
    n_binsx=7, x_label=r"Number of tight leptons per event",
    x_units=None, x_min=2, x_max=9,
    n_binsy=10, y_label=r"Number of loose leptons per event",
    y_units=None, y_min=1, y_max=11,
    z_min=0, z_max=5.5E6, z_label_size=None,
    n_contour=100)

h2_nfaillepsz1_vs_nfaillepsz2 = make_TH2F(
    "h2_nfaillepsz1_vs_nfaillepsz2",
    title=None,
    n_binsx=3, x_label=r"Number of failing leptons in Z_{1}",
    x_units=None, x_min=0, x_max=3,
    n_binsy=3, y_label=r"Number of failing leptons in Z_{2}",
    y_units=None, y_min=0, y_max=3,
    z_min=0, z_max=1E5, z_label_size=None,
    n_contour=100, center_labels=True,
    n_ticks_x_pri=2, n_ticks_y_pri=2
    )