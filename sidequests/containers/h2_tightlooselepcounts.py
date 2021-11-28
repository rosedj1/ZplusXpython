from Utils_ROOT.ROOT_classes import make_TH1F, make_TH2F

h1_nleps_perevent = make_TH1F(
    internal_name="h1_nleps_perevent",
    title=None,
    n_bins=10,
    xlabel="Number of leptons per event",
    x_min=0,
    x_max=10,
    ylabel="Number of events",
    y_min=None,
    y_max=None,
    units=None
    )

h1_n2p2f_combos = make_TH1F(
    internal_name="h1_n2p2f_combos",
    title=None,
    n_bins=6,
    xlabel="Number of 2P2F combinations per event",
    x_min=1,
    x_max=7,
    ylabel="Number of events",
    y_min=None,
    y_max=None,
    units=None
    )

h1_n3p1f_combos = make_TH1F(
    internal_name="h1_n3p1f_combos",
    title=None,
    n_bins=6,
    xlabel="Number of 3P1F combinations per event",
    x_min=1,
    x_max=7,
    ylabel="Number of events",
    y_min=None,
    y_max=None,
    units=None
    )

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

# h2_ntightleps_vs_nlooseleps = make_TH2F(
#     "h2_ntightleps_vs_nlooseleps",
#     title=None,
#     n_binsx=10, x_label=r"Number of loose leptons per event",
#     x_units=None, x_min=2, x_max=12,
#     n_binsy=8, y_label=r"Number of tight leptons per event",
#     y_units=None, y_min=0, y_max=8,
#     z_min=0, z_max=5.5E6, z_label_size=None,
#     n_contour=100)

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