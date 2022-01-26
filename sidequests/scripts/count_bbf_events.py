from sidequests.classes.filecomparer import FileRunLumiEvent

cr = '3p1f'

if cr == '3p1f':
    n_failed_leps = 1
elif cr == '2p2f':
    n_failed_leps = 2

finalstate = 1
For counting Filippo's file.
for evt in t: 
    if evt.nZXCRFailedLeptons == 1: 
        if evt.finalState == finalstate: 
            if evt.passedZXCRSelection: 
                m4l = evt.mass4l 
                if (105 < m4l) and (m4l < 140): 
                    run = evt.Run 
                    lumisect = evt.LumiSect 
                    event = evt.Event 
                    ls_tup_fil.extend([(run, lumisect, event,)])

frle_fil = FileRunLumiEvent(txt=infile_txt_fili)
frle_jake_withquartets = FileRunLumiEvent(txt=infile_txt_jake)

# For counting Jake's file.
len(frle_fil.analyze_evtids(frle_jake_withquartets, event_type="common"))