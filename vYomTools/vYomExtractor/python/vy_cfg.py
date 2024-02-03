import FWCore.ParameterSet.Config as cms
import FWCore.Utilities.FileUtils as FileUtils
import FWCore.PythonUtilities.LumiList as LumiList
import FWCore.ParameterSet.Types as CfgTypes
import sys

# sys.argv will have pattern like this-> [cmsRun vy_cfg.py inputurl=root://eospublic.cern.ch//eos/opendata/cms/Run2015D/SingleElectron/MINIAOD/08Jun2016-v1/10000/001A703B-B52E-E611-BA13-0025905A60B6.root True]
# we want inputurl to be in cms.untracked.vstring format
isData = False
if len(sys.argv) > 3:
	isData = sys.argv[3]
else:
	isData = False
	print("isData not provided, assuming it to be MC")
	


inputurl = sys.argv[2]
sourceurl = cms.untracked.vstring(inputurl)
print(sourceurl)
isData =True


process = cms.Process("raman")

#---- Configure the framework messaging system
#---- https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideMessageLogger
process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.cerr.threshold = "WARNING"
process.MessageLogger.categories.append("raman")
process.MessageLogger.cerr.INFO = cms.untracked.PSet(
    limit=cms.untracked.int32(-1))
process.options = cms.untracked.PSet(wantSummary=cms.untracked.bool(True))

#---- Select the maximum number of events to process (if -1, run over all events)
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(100) )

#---- Needed configuration for dealing with transient tracks if required
process.load("TrackingTools/TransientTrack/TransientTrackBuilder_cfi")
process.load("Configuration.Geometry.GeometryIdeal_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")

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

#---- Define the test source files to be read using the xrootd protocol (root://), or local files (file:)
process.source = cms.Source("PoolSource", fileNames = sourceurl)
if isData:
    process.source.fileNames = sourceurl
	
    #---- Apply the data quality JSON file filter. This example is for 2015 data
    #---- It needs to be done after the process.source definition
    #---- Make sure the location of the file agrees with your setup
    goodJSON = "/code/CMSSW_7_6_7/src/PhysObjectExtractorTool/PhysObjectExtractor/data/Cert_13TeV_16Dec2015ReReco_Collisions15_25ns_JSON_v2.txt"
    myLumis = LumiList.LumiList(filename=goodJSON).getCMSSWString().split(",")
    process.source.lumisToProcess = CfgTypes.untracked(CfgTypes.VLuminosityBlockRange())
    process.source.lumisToProcess.extend(myLumis)


#----- Configure POET analyzers -----#
process.myelectrons = cms.EDAnalyzer('ElectronAnalyzer', 
                                     electrons = cms.InputTag("slimmedElectrons"), 
                                     vertices=cms.InputTag("offlineSlimmedPrimaryVertices"))

process.mymuons = cms.EDAnalyzer('MuonAnalyzer', 
                                 muons = cms.InputTag("slimmedMuons"), 
                                 vertices=cms.InputTag("offlineSlimmedPrimaryVertices"))



#----- RUN THE JOB! -----#
process.TFileService = cms.Service("TFileService", fileName=cms.string("myoutput.root"))

if isData:
	process.p = cms.Path(process.myelectrons)
else:
	process.p = cms.Path(process.myelectrons)
