def PartOrigin(isData, lep_matchedR03_PdgId, lep_matchedR03_MomId, lep_matchedR03_MomMomId, lep_Hindex, lep_id, FillValue, FillWeight, Hist_prompt, Hist_fakes, Hist_BDfakes,  Hist_conv, isZX):
    """
    May fill Hist_prompt.
    May fill Hist_fakes.
    Only works for MC.
    
    """
    n_pass = 0
    n_nonprompttaus = 0
    n_nonpromptconv = 0
    n_nonpromptformphot = 0
    n_prompt = 0
    n_bdfake = 0
    n_fakes = 0
    n_others = 0  
    if not isData:
        n_pass = n_pass + 1
        n=0
        test_particle_origin = ( (abs(lep_matchedR03_PdgId[lep_Hindex[2]])==15) or (abs(lep_matchedR03_MomId[lep_Hindex[2]])==15) or (abs(lep_matchedR03_MomId[lep_Hindex[2]])==15) )
        n = n + test_particle_origin
        
        if (n >= 1):
            n_nonprompttaus = n_nonprompttaus + 1
            if not isZX:
                Hist_fakes.Fill(FillValue,FillWeight)
        else:
            n = 0
            test_particle_origin = ( lep_matchedR03_PdgId[lep_Hindex[2]]==22 and (abs(lep_matchedR03_MomId[lep_Hindex[2]])==11 or abs(lep_matchedR03_MomId[lep_Hindex[2]])==13 or abs(lep_matchedR03_MomId[lep_Hindex[2]])==15) )
            n = n + test_particle_origin
            
            if (n==1): 
                n_nonpromptconv = n_nonpromptconv + 1
                if not (isZX):
                    Hist_conv.Fill(FillValue,FillWeight)
            else:
                n=0
                test_particle_origin = ( lep_matchedR03_PdgId[lep_Hindex[2]]==22 and not (abs(lep_matchedR03_MomId[lep_Hindex[2]])==11 or abs(lep_matchedR03_MomId[lep_Hindex[2]])==13 or abs(lep_matchedR03_MomId[lep_Hindex[2]])==15) )
                n = n + test_particle_origin
                
                # n+=(lep_matchedR03_PdgId[lep_Hindex[2]]==22)and((abs(lep_matchedR03_MomId[lep_Hindex[2]])==11)or(abs(lep_matchedR03_MomId[lep_Hindex[i]])==13));
                # n+=(lep_matchedR03_MomId[lep_Hindex[2]]==22)and((abs(lep_matchedR03_PdgId[lep_Hindex[2]])==11)or(abs(lep_matchedR03_PdgId[lep_Hindex[i]])==13));
                # n+=(lep_matchedR03_MomMomId[lep_Hindex[2]]==22)and((abs(lep_matchedR03_MomId[lep_Hindex[2]])==11)or(abs(lep_matchedR03_MomId[lep_Hindex[i]])==13));
                
                if (n >= 1):
                    if  not (isZX):
                        Hist_fakes.Fill(FillValue,FillWeight)
                    n_nonpromptformphot = n_nonpromptformphot + 1
        
                else:
                    n=0
                    
                    test_particle_origin_1 = ( lep_matchedR03_PdgId[lep_Hindex[2]]==23 )
                    test_particle_origin_2 = ( ( (lep_matchedR03_MomId[lep_Hindex[2]]==23) or (abs(lep_matchedR03_MomId[lep_Hindex[2]])==24) or (lep_matchedR03_MomId[lep_Hindex[2]]==25) ) and (lep_matchedR03_PdgId[lep_Hindex[2]]==lep_id[lep_Hindex[2]]) )
                    test_particle_origin_3 = ( ( (lep_matchedR03_MomMomId[lep_Hindex[2]]==23) or (abs(lep_matchedR03_MomMomId[lep_Hindex[2]])==24) or (lep_matchedR03_MomMomId[lep_Hindex[2]]==25) ) and ((lep_matchedR03_PdgId[lep_Hindex[2]]==lep_id[lep_Hindex[2]]) and (lep_matchedR03_MomId[lep_Hindex[2]]==lep_id[lep_Hindex[2]])))

                    n = n + test_particle_origin_1 + test_particle_origin_2 + test_particle_origin_3
                    if ( n >= 1 ):
                    
                        if not(isZX):
                            Hist_prompt.Fill(FillValue,FillWeight)
                        n_prompt = n_prompt + 1
                        
                    else:
                        n=0

                        test_particle_origin_1 = ((abs(lep_matchedR03_PdgId[lep_Hindex[2]])>410)and(abs(lep_matchedR03_PdgId[lep_Hindex[2]])<436))or((abs(lep_matchedR03_PdgId[lep_Hindex[2]])>10410)and(abs(lep_matchedR03_PdgId[lep_Hindex[2]])<10433)) or ((abs(lep_matchedR03_PdgId[lep_Hindex[2]])>20412)and(abs(lep_matchedR03_PdgId[lep_Hindex[2]])<20434))
                        
                        test_particle_origin_2 = ((abs(lep_matchedR03_PdgId[lep_Hindex[2]])>510)and(abs(lep_matchedR03_PdgId[lep_Hindex[2]])<546))or((abs(lep_matchedR03_PdgId[lep_Hindex[2]])>10510)and(abs(lep_matchedR03_PdgId[lep_Hindex[2]])<10544)) or ((abs(lep_matchedR03_PdgId[lep_Hindex[2]])>20512)and(abs(lep_matchedR03_PdgId[lep_Hindex[2]])<20544))
                        
                        
                        test_particle_origin_3 = ((abs(lep_matchedR03_MomId[lep_Hindex[2]])>410)and(abs(lep_matchedR03_MomId[lep_Hindex[2]])<436))or((abs(lep_matchedR03_MomId[lep_Hindex[2]])>10410)and(abs(lep_matchedR03_MomId[lep_Hindex[2]])<10433)) or ((abs(lep_matchedR03_MomId[lep_Hindex[2]])>20412)and(abs(lep_matchedR03_MomId[lep_Hindex[2]])<20434))
                        
                        test_particle_origin_4 = ((abs(lep_matchedR03_MomId[lep_Hindex[2]])>510)and(abs(lep_matchedR03_MomId[lep_Hindex[2]])<546))or((abs(lep_matchedR03_MomId[lep_Hindex[2]])>10510)and(abs(abs(lep_matchedR03_MomId[lep_Hindex[2]]))<10544)) or ((abs(lep_matchedR03_MomId[lep_Hindex[2]])>20512)and(abs(lep_matchedR03_MomId[lep_Hindex[2]])<20544))
                        
                        
                        test_particle_origin_5 = ((abs(lep_matchedR03_MomMomId[lep_Hindex[2]])>410)and(abs(lep_matchedR03_MomMomId[lep_Hindex[2]])<436))or((abs(lep_matchedR03_MomMomId[lep_Hindex[2]])>10410)and(abs(lep_matchedR03_MomMomId[lep_Hindex[2]])<10433)) or ((abs(lep_matchedR03_MomMomId[lep_Hindex[2]])>20412)and(abs(lep_matchedR03_MomMomId[lep_Hindex[2]])<20434))
                        
                        test_particle_origin_6 = ((abs(lep_matchedR03_MomMomId[lep_Hindex[2]])>510)and(abs(lep_matchedR03_MomMomId[lep_Hindex[2]])<546))or((abs(lep_matchedR03_MomMomId[lep_Hindex[2]])>10510)and(abs(lep_matchedR03_MomMomId[lep_Hindex[2]])<10544)) or ((abs(lep_matchedR03_MomMomId[lep_Hindex[2]])>20512)and(abs(lep_matchedR03_MomMomId[lep_Hindex[2]])<20544))
                        
                        n = n + test_particle_origin_1 + test_particle_origin_2 + test_particle_origin_3 + test_particle_origin_4 + test_particle_origin_5 + test_particle_origin_6
                        
                        if ( n >= 1 ) :
                            
                            if not(isZX):
                                Hist_BDfakes.Fill(FillValue,FillWeight)
                            
                            n_bdfake = n_bdfake + 1

                        else:
                            n = 0
                            
                            test_particle_origin_1 = ((abs(lep_matchedR03_PdgId[lep_Hindex[2]])<10)or(abs(lep_matchedR03_PdgId[lep_Hindex[2]])>100))
                            test_particle_origin_2 = ((abs(lep_matchedR03_MomId[lep_Hindex[2]])<10)or(abs(lep_matchedR03_MomId[lep_Hindex[2]])>100))
                            test_particle_origin_3 = ((abs(lep_matchedR03_MomMomId[lep_Hindex[2]])<10)or(abs(lep_matchedR03_MomMomId[lep_Hindex[2]])>100))

                            if ( n >= 1 ):
                                n_fakes = n_fakes + 1
                                
                                if not(isZX):
                                    Hist_fakes.Fill(FillValue,FillWeight)
                            
                            else:
                                n = 0
                                
                                if not(isZX):
                                    Hist_fakes.Fill(FillValue,FillWeight)
                                
                                n_others = n_others + 1
