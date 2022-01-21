from Utils_ROOT.ROOT_classes import make_TH1F, make_TH2F

h1_nleps_perevent = make_TH1F(internal_name="h1_nleps_perevent", title=None, n_bins=10, xlabel="Number of leptons per event", x_min=0, x_max=10, ylabel="Number of events", y_min=None, y_max=None, units=None)

h1_data_2p2f_m4l = make_TH1F(internal_name="h1_data_2p2f_m4l", title="Data Raw: 2P2F", n_bins=70, xlabel=r"m_{4l}", x_min=105, x_max=140, ylabel=None, y_min=None, y_max=None, units="GeV")
h1_data_3p1f_m4l = make_TH1F(internal_name="h1_data_3p1f_m4l", title="Data Raw: 3P1F", n_bins=70, xlabel=r"m_{4l}", x_min=105, x_max=140, ylabel=None, y_min=None, y_max=None, units="GeV")
h1_data_2p2fpred_m4l = make_TH1F(internal_name="h1_data_2p2fpred_m4l", title="Data Prediction: 2P2F", n_bins=70, xlabel=r"m_{4l}", x_min=105, x_max=140, ylabel=None, y_min=None, y_max=None, units="GeV")
h1_data_3p1fpred_m4l = make_TH1F(internal_name="h1_data_3p1fpred_m4l", title="Data Prediction: 3P1F", n_bins=70, xlabel=r"m_{4l}", x_min=105, x_max=140, ylabel=None, y_min=None, y_max=None, units="GeV")
h1_data_2p2fin3p1f_m4l = make_TH1F(internal_name="h1_data_2p2fin3p1f_m4l", title="Data: 2P2F contribution to 3P1F", n_bins=70, xlabel=r"m_{4l}", x_min=105, x_max=140, ylabel=None, y_min=None, y_max=None, units="GeV")

h1_data_n2p2f_combos = make_TH1F(internal_name="h1_data_n2p2f_combos", title="", n_bins=11, xlabel="Number of 2P2F Lepton Quartets per Event", x_min=0, x_max=11, ylabel=None, y_min=None, y_max=None, units=None)
h1_data_n3p1f_combos = make_TH1F(internal_name="h1_data_n3p1f_combos", title="", n_bins=6,  xlabel="Number of 3P1F Lepton Quartets per Event", x_min=0, x_max=6, ylabel=None,  y_min=None, y_max=None, units=None)

h1_zz_2p2f_m4l = make_TH1F(internal_name="h1_zz_2p2f_m4l", title="MC ZZ: 2P2F", n_bins=40, xlabel=r"m_{4l}", x_min=70, x_max=870, ylabel=None, y_min=None, y_max=None, units="GeV")
h1_zz_3p1f_m4l = make_TH1F(internal_name="h1_zz_3p1f_m4l", title="MC ZZ: 3P1F", n_bins=40, xlabel=r"m_{4l}", x_min=70, x_max=870, ylabel=None, y_min=None, y_max=None, units="GeV")
h1_zz_2p2fpred_m4l = make_TH1F(internal_name="h1_zz_2p2fpred_m4l", title="MC ZZ: 2P2F", n_bins=70, xlabel=r"m_{4l}", x_min=105, x_max=140, ylabel=None, y_min=None, y_max=None, units="GeV")
h1_zz_3p1fpred_m4l = make_TH1F(internal_name="h1_zz_3p1fpred_m4l", title="MC ZZ: 3P1F", n_bins=70, xlabel=r"m_{4l}", x_min=105, x_max=140, ylabel=None, y_min=None, y_max=None, units="GeV")
h1_zz_n2p2f_combos = make_TH1F(internal_name="h1_zz_n2p2f_combos", title="", n_bins=11, xlabel="Number of 2P2F Lepton Quartets per Event", x_min=0, x_max=11, ylabel=None, y_min=None, y_max=None, units=None)
h1_zz_n3p1f_combos = make_TH1F(internal_name="h1_zz_n3p1f_combos", title="", n_bins=6,  xlabel="Number of 3P1F Lepton Quartets per Event", x_min=0, x_max=6, ylabel=None,  y_min=None, y_max=None, units=None)
