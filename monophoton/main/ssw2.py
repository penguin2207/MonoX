#!/usr/bin/env python

import sys
import os
import socket

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
from datasets import allsamples
import main.selectors as selectors
import main.plotconfig as plotconfig
import config
from subprocess import Popen, PIPE
import shutil
from glob import glob

defaultSelectors = {
    'monoph': selectors.candidate,
    'signalRaw': selectors.signalRaw,
    'efake': selectors.eleProxy,
    'hfake': selectors.hadProxy,
    'hfakeUp': selectors.hadProxyUp,
    'hfakeDown': selectors.hadProxyDown,
    'purity': selectors.purity,
    'purityUp': selectors.purityUp,
    'purityDown': selectors.purityDown,
    'gjets': selectors.gjets,
    'halo': selectors.halo,
    'trivialShower': selectors.trivialShower,
    'dimu': selectors.dimuon,
    'monomu': selectors.monomuon,
    'monomuHfake': selectors.monomuonHadProxy,
    'diel': selectors.dielectron,
    'monoel': selectors.monoelectron,
    'monoelHfake': selectors.monoelectronHadProxy,
    'elmu': selectors.oppflavor,
    'eefake': selectors.zee,
    'wenu': selectors.wenuall,
    'zeeJets': selectors.zeeJets,
    'zmmJets': selectors.zmmJets
}

def defaults(regions):
    return [(region, defaultSelectors[region]) for region in regions]

def applyMod(modifier, regions):
    result = []
    for entry in regions:
        if type(entry) is tuple:
            region, selector = entry
        else:
            region = entry
            selector = defaultSelectors[region]

        result.append((region, modifier(selector)))

    return result

sphLumi = sum(allsamples[s].lumi for s in ['sph-16b-r', 'sph-16c-r', 'sph-16d-r', 'sph-16e-r', 'sph-16f-r', 'sph-16g-r', 'sph-16h'])

data_sph = ['monoph', 'efake', 'hfake', 'hfakeUp', 'hfakeDown', 'purity', 'purityUp', 'purityDown', 'gjets', 'dimu', 'diel', 'monomu', 'monoel', 'halo', 'trivialShower']
# data_sph = ['monoph', 'efake', 'hfake', 'hfakeUp', 'hfakeDown', 'dimu', 'diel', 'monomu', 'monoel', 'halo', 'trivialShower']
data_smu = ['dimu', 'monomu', 'monomuHfake', 'elmu', 'zmmJets'] # are SinglePhoton triggers in this PD? (do the samples know about them, obviously they are not used to define it)
data_sel = ['diel', 'monoel', 'monoelHfake', 'eefake', 'zeeJets'] # are SinglePhoton triggers in this PD? (do the samples know about them, obviously they are not used to define it)
mc_cand = ['monoph'] # , 'purity']
mc_qcd = ['hfake', 'hfakeUp', 'hfakeDown', 'purity', 'purityUp', 'purityDown', 'gjets'] 
mc_sig = ['monoph', 'purity'] # , 'signalRaw']
mc_lep = ['monomu', 'monoel']
mc_dilep = ['dimu', 'diel', 'elmu', 'zmmJets', 'zeeJets']

wlnu = applyMod(selectors.wlnu, applyMod(selectors.genveto, mc_cand)) + applyMod(selectors.genveto, mc_lep) + defaults(['wenu', 'zmmJets', 'zeeJets'])

selectors = {
    # Data 2016
    'sph-16b-r': defaults(data_sph),
    'sph-16c-r': defaults(data_sph),
    'sph-16d-r': defaults(data_sph),
    'sph-16e-r': defaults(data_sph),
    'sph-16f-r': defaults(data_sph),
    'sph-16g-r': defaults(data_sph),
    'sph-16h': defaults(data_sph),
    # MC for signal region
    'znng-130': applyMod(selectors.kfactor, mc_sig),
    'wnlg-130': applyMod(selectors.kfactor, mc_sig + mc_lep),
    'zllg-130': applyMod(selectors.kfactor, mc_sig + mc_lep + mc_dilep),
    'wglo': applyMod(selectors.wglo, mc_cand + mc_lep),
    'wglo-500': defaults(mc_cand + mc_lep),
    'gj-100': applyMod(selectors.kfactor, mc_qcd + mc_cand),
    'gj-200': applyMod(selectors.kfactor, mc_qcd + mc_cand),
    'gj-400': applyMod(selectors.kfactor, mc_qcd + mc_cand),
    'gj-600': applyMod(selectors.kfactor, mc_qcd + mc_cand),
    'gg-40': defaults(mc_cand + mc_lep + mc_dilep),
    'gg-80': defaults(mc_cand + mc_lep + mc_dilep),
    'tt': defaults(mc_cand + mc_lep + mc_dilep),
    'tg': defaults(mc_cand + mc_lep),
    'ttg': defaults(mc_cand + mc_lep + mc_dilep),
    'wwg': defaults(mc_cand + mc_lep + mc_dilep),
    'ww': defaults(mc_cand + mc_lep + mc_dilep),
    'wz': defaults(mc_cand + mc_lep + mc_dilep),
    'zz': defaults(mc_cand + mc_lep + mc_dilep),
    'wlnu-100': wlnu,
    'wlnu-200': wlnu,
    'wlnu-400': wlnu,
    'wlnu-600': wlnu,
    'wlnu-800': wlnu,
    'wlnu-1200': wlnu,
    'wlnu-2500': wlnu,
    'dy-50-100': applyMod(selectors.genveto, mc_cand + mc_lep + mc_dilep),
    'dy-50-200': applyMod(selectors.genveto, mc_cand + mc_lep + mc_dilep),
    'dy-50-400': applyMod(selectors.genveto, mc_cand + mc_lep + mc_dilep),
    'dy-50-600': applyMod(selectors.genveto, mc_cand + mc_lep + mc_dilep),
    'dy-50-800': applyMod(selectors.genveto, mc_cand + mc_lep + mc_dilep),
    'dy-50-1200': applyMod(selectors.genveto, mc_cand + mc_lep + mc_dilep),
    'dy-50-2500': applyMod(selectors.genveto, mc_cand + mc_lep + mc_dilep),
    'qcd-200': defaults(mc_cand + mc_qcd + mc_dilep + mc_lep),
    'qcd-300': defaults(mc_cand + mc_qcd + mc_dilep + mc_lep),
    'qcd-500': defaults(mc_cand + mc_qcd + mc_dilep + mc_lep),
    'qcd-700': defaults(mc_cand + mc_qcd + mc_dilep + mc_lep),
    'qcd-1000': defaults(mc_cand + mc_qcd + mc_dilep + mc_lep),
    'qcd-1500': defaults(mc_cand + mc_qcd + mc_dilep + mc_lep),
    'qcd-2000': defaults(mc_cand + mc_qcd + mc_dilep + mc_lep)
}

# all the rest are mc_sig
for sname in allsamples.names():
    if sname not in selectors:
        selectors[sname] = defaults(mc_sig)

def processSampleNames(_inputNames, _selectorKeys, _plotConfig = ''):
    snames = []

    if _plotConfig:
        # if a plot config is specified, use the samples for that
        snames = plotconfig.getConfig(_plotConfig).samples()

    else:
        snames = _inputNames

    # handle special group names
    if 'all' in snames:
        snames.remove('all')
        snames = _selectorKeys
    if 'data16' in snames:
        snames.remove('data16')
        snames += [key for key in _selectorKeys if '16' in key and allsamples[key].data]
    if 'bkgd' in snames:
        snames.remove('bkgd')
        snames += [key for key in _selectorKeys if not allsamples[key].data and not key.startswith('dm') and not key.startswith('add') and not key.endswith('-d')]
    if 'dmfs' in snames:
        snames.remove('dmfs')
        snames += [key for key in _selectorKeys if key.startswith('dm') and key[3:5] == 'fs']
    if 'dm' in snames:
        snames.remove('dm')
        snames += [key for key in _selectorKeys if key.startswith('dm') and not key[3:5] == 'fs']
    if 'add' in snames:
        snames.remove('add')
        snames += [key for key in _selectorKeys if key.startswith('add')]
    if 'fs' in snames:
        snames.remove('fs')
        snames += [key for key in _selectorKeys if 'fs' in key]

    # filter out empty samples
    for name in list(snames):
        if '*' in name: # wild card
            snames.remove(name)
            snames.extend([s.name for s in allsamples.getmany(name)])
        try:
            samp = allsamples[name]
        except KeyError:
            print name, "is not in datasets.csv. Removing it from the list of samples to run over."
            snames.remove(name)
            

    snames = [name for name in snames if allsamples[name].sumw != 0.]

    return snames

if __name__ == '__main__':

    from argparse import ArgumentParser
    import json
    
    argParser = ArgumentParser(description = 'Plot and count')
    argParser.add_argument('snames', metavar = 'SAMPLE', nargs = '*', help = 'Sample names to skim.')
    argParser.add_argument('--list', '-L', action = 'store_true', dest = 'list', help = 'List of samples.')
    argParser.add_argument('--plot-config', '-p', metavar = 'PLOTCONFIG', dest = 'plotConfig', default = '', help = 'Run on samples used in PLOTCONFIG.')
    argParser.add_argument('--eos-input', '-e', action = 'store_true', dest = 'eosInput', help = 'Specify that input needs to be read from eos.')
    argParser.add_argument('--nentries', '-N', metavar = 'N', dest = 'nentries', type = int, default = -1, help = 'Maximum number of entries.')
    argParser.add_argument('--files', '-f', metavar = 'nStart nEnd', dest = 'files', nargs = 2, type = int, default = [], help = 'Range of files to run on.')
    
    args = argParser.parse_args()
    sys.argv = []

    import ROOT

    ROOT.gSystem.Load(config.libsimpletree)
    ROOT.gSystem.AddIncludePath('-I' + config.dataformats + '/interface')
    ROOT.gSystem.AddIncludePath('-I' + config.dataformats + '/tools')
    ROOT.gSystem.AddIncludePath('-I' + os.path.dirname(basedir) + '/common')

    compiled = ROOT.gROOT.LoadMacro(thisdir + '/Skimmer.cc+')
    # doesn't seem to be returning different values if compilation fails :(
    if (compiled < 0 ):
        print "Couldn't compile Skimmer.cc. Quitting."
        sys.exit()

    snames = processSampleNames(args.snames, selectors.keys(), args.plotConfig)

    if args.list:
        print ' '.join(sorted(snames))
        # for sname in sorted(snames):
            # print sname
        sys.exit(0)
    
    skimmer = ROOT.Skimmer()

    if not os.path.exists(config.skimDir):
        os.makedirs(config.skimDir)

    if args.files:
        nStart = args.files[0]
        nEnd = args.files[1]
    else:
        nStart = -1
        nEnd = 100000

    for sname in snames:
        sample = allsamples[sname]
        print 'Starting sample %s (%d/%d)' % (sname, snames.index(sname) + 1, len(snames))
    
        skimmer.reset()
    
        tree = ROOT.TChain('events')

        if os.path.exists(config.photonSkimDir + '/' + sname + '.root'):
            print 'Reading', sname, 'from', config.photonSkimDir
            tree.Add(config.photonSkimDir + '/' + sname + '.root')

        else:
            if args.eosInput:
                sourceDir = sample.book + '/' + sample.fullname
            elif sample.data:
                sourceDir = config.dataNtuplesDir + sample.book + '/' + sample.fullname
            else:
                sourceDir = config.ntuplesDir + sample.book + '/' + sample.fullname

            print 'Reading', sname, 'from', sourceDir

            if args.eosInput:
                # lsCmd = ['/afs/cern.ch/project/eos/installation/0.3.84-aquamarine/bin/eos.select', 'ls', sourceDir + '/*.root']
                lsCmd = ['lcg-ls', '-b', '-D', 'srmv2', 'srm://srm-eoscms.cern.ch:8443/srm/v2/server?SFN='+sourceDir]
                listFiles = Popen(lsCmd, stdout=PIPE, stderr=PIPE)
            
                """
                (lout, lerr) = listFiles.communicate()
                print lout, '\n'
                print lerr, '\n'
                sys.exit()
                """
                
                filesList = [ line for line in listFiles.stdout if line.endswith('.root\n') ] 
                pathPrefix = 'root://eoscms'
            else:
                filesList = sorted(glob(sourceDir + '/*.root'))
                
            for iF, File in enumerate(filesList):
                if iF < nStart:
                    continue
                if iF > nEnd:
                    break
                File = File.strip(' \n')
                
                if args.eosInput:
                    print pathPrefix + File
                    tree.Add(pathPrefix + File)
                else:
                    tree.Add(File)

        print tree.GetEntries(), 'entries'
        if tree.GetEntries() == 0:
            print 'Tree has no entries. Skipping.'
            continue

        selnames = []
        for rname, gen in selectors[sname]:
            selnames.append(rname)
            selector = gen(sample, rname)
            skimmer.addSelector(selector)

        if nStart >= 0:
            sname = sname + '_' + str(nStart) + '-' + str(nEnd)

        tmpDir = '/tmp/' + os.environ['USER']
        if not os.path.exists(tmpDir):
            os.makedirs(tmpDir)
        skimmer.run(tree, tmpDir, sname, args.nentries)
        for selname in selnames:
            if os.path.exists(config.skimDir + '/' + sname + '_' + selname + '.root'):
                os.remove(config.skimDir + '/' + sname + '_' + selname + '.root')
            shutil.move(tmpDir + '/' + sname + '_' + selname + '.root', config.skimDir)
