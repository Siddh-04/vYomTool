
# -----------------------------------------------------------------------------------------------
# --------------Import the needed modules
import FWCore.ParameterSet.Config as cms
import FWCore.Utilities.FileUtils as FileUtils
import FWCore.PythonUtilities.LumiList as LumiList
import FWCore.ParameterSet.Types as CfgTypes
# from FWCore.ParameterSet.VarParsing import VarParsing
import sys
from PhysicsTools.SelectorUtils.pfJetIDSelector_cfi import pfJetIDSelector
from PhysicsTools.PatAlgos.producersLayer1.jetUpdater_cff import updatedPatJetCorrFactors
from PhysicsTools.PatAlgos.producersLayer1.jetUpdater_cfi import updatedPatJets


# -------------------------------------------------------------------------------------------
# the sysargv will take argument in pattern
# cmsRun python/vYom_cfg.py <input_url> <isData (default=False)> 
#  = VarParsing('analysis') # VarParsing is the class for parsing argument 
print("____________________________________________________________")
# print("|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||")
print("                          This is vYom")
# print("|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||")
print("____________________________________________________________")
# options = VarParsing ('analysis') # VarParsing is use to parse the argument 
isData = False
print(" ")
if len(sys.argv) > 3:
	isData = sys.argv[3]
    
	print(" bThis is the Dataset -> ",isData)
else:
	isData = False
    
	print(" boolean parameter not provided, assuming it to be MC")
    
print(" ")

inputurl = sys.argv[2]
sourceurl = cms.untracked.vstring(inputurl)


# ------------------------------------------------------------------------------------------------------------------

#  Set up the process
process = cms.Process("vYom")

# ------------------------------------------------------------------------------------------------------------------
# 
process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.cerr.threshold = "WARNING"
process.MessageLogger.categories.append("vYom")
process.MessageLogger.cerr.INFO = cms.untracked.PSet(
    limit=cms.untracked.int32(-1))
process.options = cms.untracked.PSet(wantSummary=cms.untracked.bool(True))

# ----------------------------------------------------------------------------------------------
# setting maxEvents
process.maxEvents = cms.untracked.PSet(input=cms.untracked.int32(100))

# ----------------------------------------------------------------------------------------------
# #---- Needed configuration for dealing with transient tracks if required
process.load("TrackingTools/TransientTrack/TransientTrackBuilder_cfi")
process.load("Configuration.Geometry.GeometryIdeal_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")

# ----------------------------------------------------------------------------------------------

#---- These two lines are needed if you require access to the conditions database. E.g., to get jet energy corrections, trigger prescales, etc.
process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
#---- Uncomment and arrange a line like this if you are getting access to the conditions database through CVMFS snapshot files (requires installing CVMFS client)
#process.GlobalTag.connect = cms.string('sqlite_file:/cvmfs/cms-opendata-conddb.cern.ch/76X_dataRun2_16Dec2015_v0.db')
#---- If the container has local DB files available, uncomment lines like the ones below instead of the corresponding lines above
if isData: process.GlobalTag.connect = cms.string('sqlite_file:/cvmfs/cms-opendata-conddb.cern.ch/76X_dataRun2_16Dec2015_v0.db')
else: process.GlobalTag.connect = cms.string('sqlite_file:/cvmfs/cms-opendata-conddb.cern.ch/76X_mcRun2_asymptotic_RunIIFall15DR76_v1.db')
#---- The global tag must correspond to the needed epoch (comment out if no conditions needed)
if isData: process.GlobalTag.globaltag = '76X_dataRun2_16Dec2015_v0'
else: process.GlobalTag.globaltag = "76X_mcRun2_asymptotic_RunIIFall15DR76_v1"

# ----------------------------------------------------------------------------------------------
# #---- Define the source
process.source = cms.Source("PoolSource", fileNames=sourceurl)

if isData:
    process.source.fileNames = sourceurl
    goodJSON = "/code/CMSSW_7_6_7/src/vYomTools/vYomExtractor/data/Cert_13TeV_16Dec2015ReReco_Collisions15_25ns_JSON_v2.txt"
    myLumis = LumiList.LumiList(filename=goodJSON).getCMSSWString().split(",")
    process.source.lumisToProcess = CfgTypes.untracked(CfgTypes.VLuminosityBlockRange())
    process.source.lumisToProcess.extend(myLumis)

# ----------------------------------------------------------------------------------------------
#                                       Using POET Analyzer
# ---------------------------------------------------------------------------------------------
process.myelectrons = cms.EDAnalyzer('ElectronAnalyzer', 
                                     electrons = cms.InputTag("slimmedElectrons"), 
                                     vertices=cms.InputTag("offlineSlimmedPrimaryVertices"))

process.mymuons = cms.EDAnalyzer('MuonAnalyzer', 
                                 muons = cms.InputTag("slimmedMuons"), 
                                 vertices=cms.InputTag("offlineSlimmedPrimaryVertices"))

process.mytaus = cms.EDAnalyzer('TauAnalyzer', taus=cms.InputTag("slimmedTaus"))

process.myphotons = cms.EDAnalyzer('PhotonAnalyzer', photons=cms.InputTag("slimmedPhotons"))

process.mypvertex = cms.EDAnalyzer('VertexAnalyzer',
                                   vertices=cms.InputTag("offlineSlimmedPrimaryVertices"), 
                                   beams=cms.InputTag("offlineBeamSpot"))
# process.mygenparticle = cms.EDAnalyzer('GenParticleAnalyzer', 
#                                        pruned=cms.InputTag("prunedGenParticles"),
#                                        #---- Collect particles with specific "status:pdgid"
#                                        #---- if 0:0, collect them all 
#                                        input_particle = cms.vstring("1:11","1:13","1:22","2:15"))

# # ----------------------------------------------------------------------------------------------
# #---- These two lines are needed if you require access to the conditions database. E.g., to get jet energy corrections, trigger prescales, etc.
# process.load('Configuration.StandardSequences.Services_cff')
# process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
# #---- Uncomment and arrange a line like this if you are getting access to the conditions database through CVMFS snapshot files (requires installing CVMFS client)
# #process.GlobalTag.connect = cms.string('sqlite_file:/cvmfs/cms-opendata-conddb.cern.ch/76X_dataRun2_16Dec2015_v0.db')
# #---- If the container has local DB files available, uncomment lines like the ones below instead of the corresponding lines above
# if isData: process.GlobalTag.connect = cms.string('sqlite_file:/cvmfs/cms-opendata-conddb.cern.ch/76X_dataRun2_16Dec2015_v0.db')
# else: process.GlobalTag.connect = cms.string('sqlite_file:/cvmfs/cms-opendata-conddb.cern.ch/76X_mcRun2_asymptotic_RunIIFall15DR76_v1.db')
# #---- The global tag must correspond to the needed epoch (comment out if no conditions needed)
# if isData: process.GlobalTag.globaltag = '76X_dataRun2_16Dec2015_v0'
# else: process.GlobalTag.globaltag = "76X_mcRun2_asymptotic_RunIIFall15DR76_v1"


# ----------------------------------------------------------------------------------------------
# adding some stuff for jet correction

# JecString = 'MC'
# if isData: JecString = 'DATA'

# ----------------------------------------------------------------------------------------------
#                                   adding Trigger Analyzer
# ----------------------------------------------------------------------------------------------
# process.mytriggers = cms.EDAnalyzer('TriggerAnalyzer',
#                               processName = cms.string("HLT"),
#                               #---- These are example triggers for 2012
#                               #---- Wildcards * and ? are accepted (with usual meanings)
#                                #---- If left empty, all triggers will run              
#                               triggerPatterns = cms.vstring("HLT_L2DoubleMu23_NoVertex_v*","HLT_Mu12_v*", "HLT_Photon20_CaloIdVL_v*", "HLT_Ele22_CaloIdL_CaloIsoVL_v*", "HLT_Jet370_NoJetID_v*"), 
#                               triggerResults = cms.InputTag("TriggerResults","","HLT"),
#                               triggerEvent   = cms.InputTag("hltTriggerSummaryAOD","","HLT")                             
#                               )




# ----------------------------------------------------------------------------------------------
# Run the job
process.TFileService = cms.Service("TFileService", fileName=cms.string("Roo1.root"))

process.p = cms.Path(process.myelectrons + process.mymuons + process.mytaus + process.myphotons + process.mypvertex)

# ----------------------------------------------------------------------------------------------
#                        Bye Bye
# ----------------------------------------------------------------------------------------------

# process.maxEvents.input = options.maxEvents
# process.TFileService.fileName = options.outputFile
# if len(options.inputFiles) > 0:
    # process.source.fileNames=options.inputFiles
# print "||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||"
print("________________________________________________________________________________")
# print "Processing for maxEvents =  ",process.maxEvents.input
# print "Processing input files "
# for fl in process.source.fileNames:
    # print "  > ",fl

# print " "
# print "Output filename : ",process.TFileService.fileName
print ("________________________________________________________________________________")
# print "|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||"