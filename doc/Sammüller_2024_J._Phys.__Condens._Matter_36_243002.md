Journal of Physics: Condensed
Matter
TOPICAL REVIEW • OPEN ACCESS You may also like
Why neural functionals suit statistical mechanics -Biomimetic polymer fibers—function by
design
Thomas Ebbinghaus, Gregor Lang and
Thomas Scheibel
To cite this article: Florian Sammüller et al 2024 J. Phys.: Condens. Matter 36 243002
-Recombinant major ampullate spidroin-
particles as biotemplates for manganese
carbonate mineralization
Vanessa J Neubauer, Christine Kellner,
Viktoria Gruen et al.
View the article online for updates and enhancements.
-Rapid non-invasive detection of Influenza-
A-infection by multicapillary column
coupled ion mobility spectrometry
Claus Steppert, Isabel Steppert, Thomas
Bollinger et al.
This content was downloaded from IP address 104.28.133.10 on 20/09/2024 at 05:22

JournalofPhysics:CondensedMatter
J.Phys.:Condens.Matter36(2024)243002(23pp) https://doi.org/10.1088/1361-648X/ad326f
| Topical | Review |     |             |     |     |      |             |     |     |     |     |     |
| ------- | ------ | --- | ----------- | --- | --- | ---- | ----------- | --- | --- | --- | --- | --- |
| Why     | neural |     | functionals |     |     | suit | statistical |     |     |     |     |     |
mechanics
|         | Sammüller, |        | Hermann |              |     |         |     | ∗  |     |     |     |     |
| ------- | ----------- | ------ | -------- | ------------ | --- | ------- | --- | --- | --- | --- | --- | --- |
| Florian |             | Sophie |          | and Matthias |     | Schmidt |     |     |     |     |     |     |
TheoretischePhysikII,PhysikalischesInstitut,UniversitätBayreuth,D-95447Bayreuth,Germany
E-mail:Matthias.Schmidt@uni-bayreuth.de
Received29November2023,revised14February2024
Acceptedforpublication11March2024
Published21March2024
Abstract
Wedescriberecentprogressinthestatisticalmechanicaldescriptionofmany-bodysystemsvia
machinelearningcombinedwithconceptsfromdensityfunctionaltheoryandmany-body
simulations.WearguethattheneuralfunctionaltheorybySammülleretal(2023Proc.Natl
Acad.Sci.120e2312484120)givesafunctionalrepresentationofdirectcorrelationsandof
thermodynamicsthatallowsforthoroughqualitycontrolandconsistencycheckingofthe
involvedmethodsofartificialintelligence.Addressingaprototypicalsystemweherepresenta
pedagogicalapplicationtohardcoreparticleinonespatialdimension,wherePercus’exact
solutionforthefreeenergyfunctionalprovidesanunambiguousreference.Acorresponding
standalonenumericaltutorialthatdemonstratestheneuralfunctionalconceptstogetherwiththe
underlyingfundamentalsofMonteCarlosimulations,classicaldensityfunctionaltheory,
machinelearning,anddifferentialprogrammingisavailableonlineathttps://github.com/sfalmo/
NeuralDFT-Tutorial.
| Keywords: | densityfunctionaltheory,statisticalmechanics,machinelearning, |     |     |     |     |     |     |     |     |     |     |     |
| --------- | ------------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
inhomogeneousfluids,fundamentalmeasuretheory,neuralfunctionaltheory,
differentialprogramming
1. Introduction descriptionsoffundamentalphasecoexistencephenomenaby
modernstandardsofstatisticalmechanics.
Thediscoveryofthemolecularstructureofmatterwasstillin What was unknown then is that an underlying formally
itsinfancywhenvanderWaalspredictedin1893ontheoret- exact variational principle exists. This mathematical struc-
icalgroundsthatthegas–liquidinterfacehasfinitethickness. ture was recognized only much later, first quantum mechan-
Thetheoryisbasedonasquare-gradienttreatmentofthedens-
|     |     |     |     |     | ically | by  | Hohenberg | and | Kohn | [3] for the | groundstate | of a |
| --- | --- | --- | --- | --- | ------ | --- | --------- | --- | ---- | ----------- | ----------- | ---- |
ityinhomogeneitybetweenthecoexistingphases[1,2]andit many-bodysystem,subsequentlybyMermin[4]forfinitetem-
isconsistentwithvanderWaals’earliertreatmentofthegas– peratures, and then classically by Evans [5]. The variational
liquid phase separation in bulk. Both the bulk and the inter- principle forms the core of density functional theory and the
facial treatments are viewed as simple yet physically correct intervening history between the quantum [4] and classical
|     |     |     |     |     | milestones |     | [5] is | described | by  | Evans et al | [6]; much | back- |
| --- | --- | --- | --- | --- | ---------- | --- | ------ | --------- | --- | ----------- | --------- | ----- |
groundofthetheoryisgivenin[7–9].KohnandSham[10,11]
∗
Authortowhomanycorrespondenceshouldbeaddressed. re-introducedorbitalsviaaneffectivesingle-particledescrip-
|     |                  |      |                  |                | tion,                   | which | facilitates | the | efficient | treatment | of  | the many- |
| --- | ---------------- | ---- | ---------------- | -------------- | ----------------------- | ----- | ----------- | --- | --------- | --------- | --- | --------- |
|     | Original Content | from | this work may be | used under the | electronquantumproblem. |       |             |     |           |           |     |           |
termsoftheCreativeCommonsAttribution4.0licence.Any
furtherdistributionofthisworkmustmaintainattributiontotheauthor(s)and Practical applications of density functional theory require
thetitleofthework,journalcitationandDOI. one to make concrete approximations for the central
|     |     |     |     |     | 1   |     |     | ©2024TheAuthor(s).PublishedbyIOPPublishingLtd |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --------------------------------------------- | --- | --- | --- | --- |

J.Phys.:Condens.Matter36(2024)243002 TopicalReview
functional.(Werecallthatafunctionalmapsanentirefunction
to a number.) Quantum mechanically one needs to approx-
imate the exchange-correlation energy functional E [n], as
xc
dependingontheelectronicdensityprofilen(r),andclassic-
allyoneneedstogettogripswiththeexcess(overidealgas)
intrinsicHelmholtzfreeenergyF [ρ],asafunctionalofthe
exc
localparticledensityρ(r).
A broad range of relevant problems and intriguing col-
lective and self-organization effects in soft matter [12] have
been investigated on the basis of classical density functional
theory[5–9].Exemplarytopicalstudiesincludeinvestigations
of hydrophobicity [13–16], the orientation-resolved molecu-
larstructureofliquids[16],thethree-dimensionallyresolved
atomic structure of electrolytes [17, 18], and the asymptotic
decayofionicstructuralcorrelations[19].
Owingtoitsrigorousformalfoundation,densityfunctional
theoryprovidesamicroscopic,first-principlestreatmentofthe
Figure1. Illustrationofhardrodsinonespatialdimensionthatare
many-body problem. The numerical efficiency of (in prac- exposedtoaposition-dependentexternalpotentialVext (x).In
ticeoftenapproximate)implementationsallowsforexhaustive responsetotheexternalinfluenceaspatiallyinhomogeneousdensity
modelparametersweeps,forsystematicinvestigationofbulk profileρ(x)emergesinequilibriumattemperatureTandchemical
andinterfacialphasetransitions,andforthediscoveryandtra-
potentialµ.Theparticleswithpositioncoordinatesxiandparticle
indexi =1,...,NhaveradiusRanddiameterσ=2R.A
cing of scaling laws. Exact statistical mechanical sum rules
configurationisforbidden(bottomrow)ifanytwoparticlesoverlap,
[20–23] integrate themselves very naturally into the scheme i.e.iftheirmutualdistanceissmallerthantheparticlediameterσ.
andtheyprovideconsistencychecksandcanformthebasisfor
refinedapproximations.Nevertheless,atthecoreofsuchstud-
iesliesusuallyanapproximatefunctionalandhenceresorting calculation [48]. A recent perspective on these and more
to explicit many-body simulations is common in a quest for developmentswasgivenbyBurkeandco-workers[50].Huang
validationofthepredicteddensityfunctionalresults. etal[51]argueprominentlythatquantumdensityfunctional
Inline with topical developments in other branches of theory plays a special role in the wider context of the use of
science, the use of machine learning is becoming increas- artificial intelligenece methods in chemistry and in materials
ingly popular in soft matter research. Recent applications science.
of machine learning range from the characterization of soft While the central problem of quantum density functional
matter [24], reverse-engineering of colloidal self-assembly theory is to deal with the exchange and correlation effects
[25], local structure detection in colloidal systems [26], to betweenelectronsthatareexposedtotheexternalfieldgener-
the investigation of many-body potentials for isotropic [27] atedbythenuclei,classicalstatisticalmechanicsofsoftmat-
andforanisotropic[28]colloids.Briefoverviewsofmachine ter relies on a much more varied range of underlying model
learninginphysics[29]andinparticularinliquidstatetheory Hamiltonians. The effective interparticle interactions in soft
[30]weregivenrecently. mattersystemscoverawidegamutofdifferenttypesofrepuls-
Density functional theory lends itself towards machine ive and attractive, short- and long-ranged, hard-, soft-, and
learningduethenecessityoffindinganapproximationforthe penetrable-corebehaviours.
centralfunctional.Correspondingresearchwascarriedoutin Inparticularthehardcoremodelplaysaspecialrole.For
theclassical[31–42]andquantumrealms[43–51].Theclas- hard core particles the pair potential between two particles
sical work addressed liquid crystals in complex confinement is infinite if the particle pair overlaps and it vanishes other-
[31], the functional construction of a convolutional network wise. Hard core particles are relatively simple as temperat-
[32] and of an equation-learning network [33], the improve- urebecomesanirrelevantvariablewhiletheessenceofshort-
mentofthestandardmean-fieldapproximationforthethree- rangedrepulsionandtheresultingmolecularpackingremain
dimensional Lennard–Jones system [34] with the aim of captured correctly [52, 53]. The statistical mechanics of the
addressing gas solubility in nanopores [35], the use physics- bulkofone-dimensionalhardcoreparticleswassolvedearly
informed Bayesian inference [36, 37], active learning with byTonks[54].Thefreeenergyfunctionalisknownexactlydue
errorcontrol[38],andthephysicsofpatchyparticles[39]. toPercus[55–59]andhissolutionprovidesthegeneralstruc-
The quantum mechanical problem was addressed on the ture and thermodynamics of the system when exposed to an
basis of machine learning the exchange-correlation potential external potential, see figure 1 for an illustration. The math-
[43–45], testing its out-of-training transferability [43], using ematical form of Percus’ free energy functional was one of
a three-dimensional convolutional neural network construct thesourcesofinspiration[60]forRosenfeld’spowerfulfunda-
[45], considering hidden messages from molecules [46], and mentalmeasuredensityfunctionalforthree-dimensionalhard
usingtheKohn–Shamequationsalreadyduringtrainingviaa spheres [61–68]. One-dimensional hard rods are also central
regularizermethod[47].TheHamiltonianitselfwastargeted fornonequilibriumphysics[69–73]andthePercusfunctional
viadeeplearningwiththeaimofefficientelectronic-structure forms a highly useful reference for developing and testing
2

| J.Phys.:Condens.Matter36(2024)243002 |          |            |     |              |         |            |     |     |     | TopicalReview |
| ------------------------------------ | -------- | ---------- | --- | ------------ | ------- | ---------- | --- | --- | --- | ------------- |
| machine                              | learning | techniques |     | in classical | density | functional |     |     |     |               |
theory[32,33,36–38].
Inrecentwork,delasHerasetal[40]andSammülleretal
| [41] have  | put forward |       | machine | learning    | strategies | that | oper- |     |     |     |
| ---------- | ----------- | ----- | ------- | ----------- | ---------- | ---- | ----- | --- | --- | --- |
| ate on the | one-body    | level | of      | correlation | functions. | Here | we    |     |     |     |
addressindetailtheneuralfunctionaltheory[41]forinhomo-
| geneous | fluids in | equilibrium. |     | We argue | that | this approach |     |     |     |     |
| ------- | --------- | ------------ | --- | -------- | ---- | ------------- | --- | --- | --- | --- |
constitutesaneuralnetwork-basedtheory,wheremultipledif-
ferentandmutuallyintimatelyrelatedneuralfunctionalsform
agenuinetheoreticalstructurethatpermitsinvestigation,test-
ing,andtoultimatelygainprofoundinsightintothenatureof
thecoupledmany-bodyphysics.Therebythetrainingisonly
requiredforasingleneuralnetwork,fromwhichthenallfur-
| ther neural | functionals |     | are created | in  | straightforward |     | ways. |     |     |     |
| ----------- | ----------- | --- | ----------- | --- | --------------- | --- | ----- | --- | --- | --- |
Themethodallowsformulti-scaleapplication[41]asisper-
tinentformanyareasofsoftmatter[74–76].Itisfurthermore
applicabletogeneralinteractions,asexemplifiedbysuccess-
|     |     |     |     |     |     |     | Figure2. | Illustrationoftherelevantfunctionalmapsoftheneural |     |     |
| --- | --- | --- | --- | --- | --- | --- | -------- | -------------------------------------------------- | --- | --- |
fullyaddressingasupercriticalLennard–Jonesfluid[41],thus
|     |     |     |     |     |     |     | functionaltheory.TheexternalpotentialVext |     | (r)generatesa |     |
| --- | --- | --- | --- | --- | --- | --- | ----------------------------------------- | --- | ------------- | --- |
complementing analytical efforts to construct density func- one-bodydensityprofileρ(r)thatisassociatedwithaone-body
tionalapproximations.Suchworkwasbased,e.g.onhierarch- directcorrelationfunctionc (r).AtgiventemperatureT,chemical
1
icalintegralequations[77,78],onfunctionalrenormalization potentialµ,andforaspecificformoftheexternalpotentialVext (r),
MonteCarlosimulationsprovidedataforthecorrespondingdensity
| group methods | [79–81], |     | and on | fundamental | measure |     | theory                                         |     |     |             |
| ------------- | -------- | --- | ------ | ----------- | ------- | --- | ---------------------------------------------- | --- | --- | ----------- |
|               |          |     |        |             |         |     | profileρ(r)andforthedirectcorrelationfunctionc |     |     | (r).Machine |
| [82–84].      |          |     |        |             |         |     |                                                |     |     | 1           |
|               |          |     |        |             |         |     | learningisusedtorepresentthefunctionalmapρ→    |     |     | c viaadeep  |
1
Hereweusetheone-dimensionalhardcoremodeltoillus- neuralnetwork.Thefunctionaldependenceofc (r)onthedensity
1
trate the key concepts of the neural functional theory, as the profileisofmuchshorterspatialrangeascomparedtothetraining
requiredsamplingcanbeperformedeasilyandPercus’func- dataobtainedfromVext →ρ.
| tional provides | an      | analytical |        | structure  | that we | can relate | to   |     |     |     |
| --------------- | ------- | ---------- | ------ | ---------- | ------- | ---------- | ---- | --- | --- | --- |
| the neural      | theory. | The        | Percus | functional | is one  | of the     | very |     |     |     |
functionalintegrationandautomaticfunctionaldifferentiation
| few general | classical | free | energy | density | functionals |     | that is |     |     |     |
| ----------- | --------- | ---- | ------ | ------- | ----------- | --- | ------- | --- | --- | --- |
isdescribedinsections3.1and3.2,respectively.Theapplic-
analyticallyknownforacontinuummodel(seee.g.also[85,
86])andthisfactprovidesfurthermotivationforourstudy.A ation of Noether sum rules as a standalone means for qual-
|          |          |                   |     |     |              |     | ity control | of the neural network | is presented | in section 3.3. |
| -------- | -------- | ----------------- | --- | --- | ------------ | --- | ----------- | --------------------- | ------------ | --------------- |
| hands-on | tutorial | that demonstrates |     | the | key concepts |     | of con-     |                       |              |                 |
structinganeuraldirectcorrelationfunctional,generatingthe Functionalintegralsumrulesareshowninsection3.4.Abrief
overviewofkeyconceptsofneuralfunctionalrepresentations
requireddatafromMonteCarlosimulations,testingagainsta
innonequilibriumarepresentedinsection4.Wegiveconclu-
numericalimplementationofthePercusfunctional,andwork-
ingwithautomaticdifferentiationisavailableonline[42]. sionsinsection5.
| The       | paper is | structured | into | individual | subsections, |                | as  |     |     |     |
| --------- | -------- | ---------- | ---- | ---------- | ------------ | -------------- | --- | --- | --- | --- |
| described | in the   | following; | each | subsection | is           | self-contained |     |     |     |     |
1.1. Neuralfunctionalconcepts
| to a significant |     | degree | such | that Readers | are | welcome | to  |     |     |     |
| ---------------- | --- | ------ | ---- | ------------ | --- | ------- | --- | --- | --- | --- |
select the description of those topics that match their own Theneuralfunctionalframework[41]restsonacombination
interestsandindividualbackgrounds.Anoverviewofkeycon- of simulation, density functional theory, and machine learn-
cepts of the one-body neural functional approach is given in ing.Datathatcharacterizestheunderlyingmany-bodysystem
section 1.1. This hybrid method draws on classical density is generated via grand canonical Monte Carlo simulations of
functionalconcepts,assummarizedinsection1.2.Functional well-defined,butrandomexternalconditions.Basedonthese
differentiation and integration methods are described in resultstheone-bodydirectcorrelationfunctionalisconstruc-
section1.3. ted as a neural network that accepts as an input the relevant
Readerswhoareprimarilyinterestedintheuseofmachine localsectionofthedensityprofile.Thismethodallowsforvery
learningmaywanttoskiptheabovematerialandratherstart efficientdatahandlingasonlyshort-rangedcorrelationscon-
withsection2.1,wherewedescribehowtoconstructandtrain tribute;figure2depictsanillustration.
the neural correlation functional on the basis of many-body Theneuralone-bodydirectcorrelationfunctionalc (r,[ρ])
1
simulationdata.Weconcentrateonthespecificmodelofone- forms the mother network for the subsequent functional cal-
dimensionalhardcoreparticlesandcomplementandcontrast culus.Automaticallydifferentiatingthemothernetworkwith
theneuralfunctionalbytheknownexactanalyticalresultsfor respectto its density input yieldsthe two-bodydirect correl-
(r,r ′,[ρ])
thismodel,asdescribedinsection2.2.Modelapplicationsfor ation functional c 2 as a daughter functional. Two-
predicting inhomogeneous systems based on neural density body direct correlations are central in liquid state theory [8]
functionaltheoryaredescribedinsection2.3. andtheyarehererepresentedbyastandalonenumericalobject
Severalmethodsofneuralfunctionalcalculusaredescribed that is created via straightforward application of automatic
insection3.Manipulatingtheneuralcorrelationfunctionalby differentiation. This workflow is very different and arguably
3

J.Phys.:Condens.Matter36(2024)243002 TopicalReview
much simpler in practice than the standard technique of car- However, due to its computational efficiency the neural
rying out the functional differentiation analytically and then approach allows to make predictions for system sizes that
implementingtheresultingexpression(s)vianumericalcode. outscale significantly the dimensions of the original simula-
Differentiatingthedaughternetworkyieldsagranddaugh- tion box. Sammüller et al [41] describe systems of micron-
ternetwork,whichrepresentsthethree-bodydirectcorrelation sized colloids confined between parallel walls with macro-
functional c (r,r ′,r ′′,[ρ]). Again this is an independent and scopicseparationdistance.Thedensityprofileisresolvedover
3
standalone numerical computing object. Very little is known asystemsizeof1mmwithnanometricprecisiononanumer-
about three-body direct correlations, with e.g. Rosenfeld’s ical grid with 10 nm spacing. Such ‘simulation beyond the
earlyinvestigationforhardspheres[61]andthefreezingstud- box’isbothpowerfulintermsofmultiscaledescriptionofsoft
iesbyLikosandAshcroft[87,88]beingnotableexceptions. matter[74–76],butisalsoservesastemplateforthemoregen-
Theneuralfunctionalmethod[41]offersarguablyunpreced- eral situation of using artificial intelligence methods far out-
enteddetailedaccess. sidetheiroriginaltrainingrealm.
Tracing the genealogy in the reverse direction requires In order to provide quality control, the neural functional
functional integration, which is a general and standard tech- theory hence allows to carry out a second type of test. This
niqueinfunctionalcalculus.Inthepresentcaseagainaquasi- is less generic than the above benchmarking but it can nev-
standalone numerical object can be built based on mere net- ertheless provide inspiration for machine learning in wider
work evaluation and standard numerical integration, both of contexts. In the present case, the specific statistical mech-
which are fast operations. In this way, functionally integrat- anical nature of the underlying equilibrium many-body sys-
ingthemotherone-bodydirectcorrelationfunctionalcreates tem implies far-reaching mathematical structure, as it lies at
asthegrandmothertheexcessfreeenergyfunctionalF [ρ]. the very heart of Statistical Mechanics. Specifically, it is the
exc
Thismathematicalobjectistheultimategeneratingfunctional significant body of equilibrium sum rules that provide form-
inclassicaldensityfunctionaltheoryforalln-bodydirectcor- allyexactinterrelationsbetweendifferenttypesofcorrelation
relation functions [5, 8, 9]. We give more details about the functions. These sum rules hold universally, i.e. independent
interrelationships within the family of functionals below in ofthespecificinhomogeneoussituationthatisunderconsid-
section1.3. erationandtheyhenceconstituteformallyexactrelationships
When applied to the three-dimensional hard sphere fluid betweenfunctionals.
andrestrictedtoplanargeometry,suchthatthedensitydistri- Astheneuralfunctionaltheoryexpressesdirectcorrelation
butionisinhomogeneousonlyalongasinglespatialdirection, functionsusingneuralnetworkmethods,thesumrulesdirectly
the neural functional theory outperforms the best available translate to identities that connect the different neural func-
hardspheredensityfunctional(theformidableWhiteBearMk. tionals and their integrated and differentiated relatives with
II fundamental measure theory [65]) in generic inhomogen- each other. Crucially, these connections have both different
eous situations. For spatially homogeneous fluids the neural mathematicalform,aswellasdifferentphysicalmeaning,as
functionalevensurpassesthe‘veryaccurateequationofstate’ compared to the bare genealogy provided by the automatic
[8] by Carnahan and Starling [52], despite the fact that no functional differentiation and functional integration. Without
explicitinformationaboutanybulkfluidpropertieswasused overstretching the analogy, one could view the sum rules as
duringtraining. genetic testing the entire family for absence of inheritable
Formulating reliable strategies of how to test machine- disease.
learningpredictionsconstitutesingeneralacomplexyetvery Whilethebodyofstatisticalmechanicalsumrulesisboth
important task, not least in the light of ongoing and pro- significant and diverse [20–23], here we rely on the recent
jected increased use of artificial intelligence in science [51]. Noether invariance theory [90–98] as a systematic means to
Theneuralfunctionaltheoryoffersawealthofconcreteself- create both known and new functional identities from the
consistency checks besides the standard benchmarking tech- thermalinvarianceoftheunderlyingstatisticalmechanics[90,
niques. Commonly and following best practice in machine 91]. In particular from invariance against local shifting one
learning, benchmarking is performed by dividing the refer- obtains sum rules that connect different generations of dir-
encedata,ashereobtainedfrommany-bodysimulations,into ect correlation functionals with each other in both locally-
training, validation and test data. The simulations in the test resolvedandglobalform.Wepresentexemplarycasesbelow
data set have not been used during training and hence can in section 3.3. Generic sum rules that emerge from the mere
serve to assess the performance of the trained network. In inverse relationship of functional integration and functional
ourpresentmodelapplication,wecanperformtestingdirectly differentationarepresentedinsection3.4.
withrespecttotheexactPercustheory.
Assessing extrapolation capabilities beyond the under-
1.2. Introductiontoclassicaldensityfunctionaltheory
lying data set requires the availability of further refer-
ence data. In [41] this is provided by comparing (favour- Wegiveacompactaccountofsomekeyconceptsofclassical
ably) against a highly accurate bulk equation of state [89] densityfunctionaltheory;formoredetailssee[5–9].Readers
as well as comparing against free energy reference results who are primarily interested in machine learning of neural
obtainedfromsimulation-basedthermodynamicintegrationof functionalscanskipthisandthenextsubsectionanddirectly
inhomogeneoussystems. proceedtosection2.
4

J.Phys.:Condens.Matter36(2024)243002 TopicalReview
Inastatisticalmechanicaldescriptionofamany-bodysys- For a mutually interacting system, where
u(rN)̸=0,
tem the local density acts as a generic order parameter that equation (4) will not be true when replacing the ideal dens-
measurestheprobabilityoffindingaparticleataspecificloc- ity profile ρ (r) by the true density profile ρ(r) as formally
id
ation.Theformaldefinitionoftheone-bodydensitydistribu- given by equation (1). Rather the sum of the three terms on
tionasastatisticalaverageis: the left hand side of equation (4) will not vanish, but yield a
DX E nontrivialcontribution:
ρ(r)= δ(r − r i ) , (1) lnρ(r)+βV (r)−βµ=c (r), (5)
ext 1
i
wheretheone-bodydirectcorrelationfunctionc (r)isingen-
1
wherethesumoverirunsoverallNparticles,r i istheposition eral nonzero and arises due to the presence of interparticle
coordinateofparticlei
=1,...,N,andδ(·)indicatestheDirac
interactions in the system. (For hard core systems c (r) typ-
1
distribution, here in three dimensions. The angles indicate a icallyfeaturesnegativevalues.)
thermalaverageovermicrostates,whichcane.g.beefficiently The machine learning strategy described below in
carriedoutinMonteCarlosimulations. section 2.1 is based on this pragmatic access to data for
Forcompleteness,wegiveaformaldescriptionoftheequi- c (r), as obtained by direct simulation of ρ(r) on the basis
1
librium average based on the grand ensemble, where it is ofexplicitlycarryingouttheaverageinequation(1)forgiven
defined as
⟨·⟩=Tr ·
e
−β(H−µN)/Ξ.
Here the inverse temper- form of V (r) and prescribed values of the thermodynamic
ext
ature is β=1/(k B T), with the Boltzmann constant k B and parametersµandT.Astheone-bodydirectcorrelationfunc-
absolute temperature T, the Hamiltonian H, chemical poten- tion is central in the neural functional theory, we combine
tialµandPgrandpartitionsu´mΞ.´Theclassicaltraceisdefined
equations (4) and (5), which yields the following equivalent
as Tr ·= ∞ N=0 (hdNN´!)−1 ´drN dpN· , where h denotes the formfortheone-bodydirectcorrelationfunction,
Planck constant and drN dpN is a shorthand for the high- (cid:18) (cid:19)
dimensionalphasespaceintegraloverallparticlepositionsand c (r)=ln
ρ(r)
, (6)
momenta in d spatial dimensions. Pedagogical introductions 1 ρ id (r)
can be found in standard textbooks [8] and an introductory
whereρ (r)isgivenbyequation(3)withΛ=1.Equation(6)
compactaccounttogetherwithadescriptionoftheforcepoint id
has the direct interpretation of c (r) as the logarithm of the
ofviewisprovidedin[91]. 1
ratiooftheactualdensityprofileandthedensityprofileofthe
TheHamiltonianhasthefollowingstandardform:
ideal gas under identical conditions, as given by the external
X p2 (cid:0) (cid:1) X potentialandthermodynamicstatepoint.
H= i +u rN + V (r), (2) In alternative terminology [8] one defines the intrinsic
ext i
i 2m i chemical potential as µ int (r)=µ− V ext (r). The intrinsic
chemical potential and the one-body direct correlation
wherep isthemomentumofparticlei,theinterparticleinter- function are related trivially to each other via µ (r)=
i int
action potential u(rN) depends on all position coordinates k T[lnρ(r)− c (r)] as is obtained straightforwardly by re-
B 1
rN=r 1 ,...,r N , and V ext (r) is an external potential energy arrangingequation(5).
function that depends on position r. Hence the sum in Thepractical,computational,andconceptualadvantageof
equation (2) comprises kinetic, interparticle, and external density functional theory lies in avoiding the explicit occur-
energycontributions.Forthecommoncaseofparticlesinter- renceofthehigh-dimensionalphasespaceintegralthatunder-
actingviaapairpotentialϕ(r)thatonlydependsontheinter- lies thermal averages; we recall the definition of the dens-
pParticledistancer,theinterparticleenergyreducestou(rN)=
ity profile (1) as such an expectation value. Instead, and
ij(̸=)
ϕ(|
r i
−
r j
|)/2wherethedoublesumrunsonlyoverdis-
without any principal loss of information, one works with
tinctparticlepairsijwithi
̸=jandthefactor1/2correctsfor
functionaldependencies.Ratherthanmerepoint-wisedepend-
doublecounting. encies,suchasbetweenthefunctionsρ(r),V (r),andc (r)
ext 1
For the ideal gas the interparticle interactions vanish, thatholdateachpointr,seeequation(5),afunctionaldepend-
u(rN)≡
0,andthedensityprofileisgivenbythegeneralized ence is on the entirety of a function and it has in general a
barometriclaw[8]: nonlocalandnonlinearstructure.
Density functional theory is specifically based on the fact
ρ (r)=e
−β(Vext (r)−µ)/Λd,
(3) [3–5] that for a given type of fluid, as characterized by its
id
interparticle interaction potential u(rN), and known thermo-
whereΛdenotesthethermaldeBrogliewavelength,whichin dynamicparametersµandT,theformofdensityprofileρ(r)
thepresentclassicalcasecanbesettoΛ=σ,withσdenoting issufficienttodeterminetheentiretyoftheexternalpotential
theparticlesize;forsimplicityofnotationhereweuseΛ=1. V
ext
(r).Henceauniquefunctionalmapexists[3–5]:
Taking the logarithm of equation (3) and collecting all
ρ→ V . (7)
termsonthelefthandsidegivesthefollowingidealgaschem- ext
icalpotentialbalance: Hereweomitthepositionargumentsonbothsidestoreflect
in the notation that the functional map relates the entirety of
lnρ id (r)+βV ext (r)−βµ=0. (4) thedensityprofiletotheentiretyoftheexternalpotential.
5

J.Phys.:Condens.Matter36(2024)243002 TopicalReview
Applyingequation(7)totheexternalpotential,asitoccurs
in equation (5), implies that the left hand side is determ-
inedfromknowledgeofthedensityprofilealone,inprinciple
withoutanyneedforaprioriknowledgeoftheformofV (r).
ext
Viatheidentity(5)wecanconcludetheexistenceofthemap:
ρ→ c , (8)
1
wheretheentiretyofthedensityprofiledeterminestheentirety
ofthedirectcorrelationfunction.Asaconsequencetheone-
body direct correlation function actually is a density func-
tional, c (r,[ρ]), where the brackets indicate the functional
1
dependence, i.e. on the entirety of the argument function,
here ρ(r). We will discuss below more explicitly that the
dependence is effectively short-ranged for the case of short-
rangedinterparticleinteractionpotentialsandthatthiscanbe
exploitedtogreateffectintheneuralnetworkmethodology.
Figure3. Illustrationoffourdifferentgenerationsofdensity
functionals.ShownaretheexcessfreeenergyfunctionalFexc [ρ]and
1.3. Densityfunctionalderivativesandintegrals theone-,two-,andthree-bodydirectcorrelationfunctionals.
U´pwarda´rrowsindicatetherelationshipviafunctionalintegration
While we have emphasized above the role of the one-body drρ(r) 1dawiththeintegrandbeingevaluatedatthescaled
0
direct correlation functional c (r,[ρ]), primarily due to c (r) densityaρ(r).Downwardarrowsindicatefunctionaldifferentiation
1 1
beingdirectlymeasurableviaequation(6),onetypicallyrather δ/δρ(r).Theneuralfunctionaltheoryisbasedontrainingc 1 (r,[ρ])
asthegeneratingmotherfunctional.Implementingthearrowed
starts with a parent functional, the excess free energy func-
operationsonlyrequireshigh-levelcode.Theresultingneural
tional F [ρ], in standard accounts of classical density func-
exc networks,aswellasfunctionalsderivedfromanalytical
tional theory. The relationship of F exc [ρ] and c 1 (r,[ρ]) is expressions,arehighlyperformant.
establishedviafunctionalcalculus.Functionaldifferentiation,
see [9] for a practitioner’s account, yields additional posi-
tion dependence and we use the notation δ/δρ(r) to denote profile,withasimplelinearrelationshipρ a (r)=aρ(r).Hence
the functional derivative with respect to the function ρ(r). the parameter value a=0 corresponds to vanishing density
Functionalintegrationistheinverseoperation.Wegiveabrief anda=1reproducesthetargetdensityprofile,asitoccursin
description of the functional relationships in the following. theargumentofβF exc [ρ]onthelefthandsideofequation(9).
An overview is illustrated in figure 3 and we will return for We emphasize that the integral over a in equation (9) is a
abroaderaccountbelowinsection3. simpleone-dimensionalintegraloverthecouplingparameter
The method of automatic differentiation [99] is an integ- a.Theconsistencybetweenequations(9)and(10)isdemon-
ral part of the new computing paradigm of differentiable stratedbelowinsection3.4.
programming [100]. Automatic differentiation is based on a The perhaps seemingly very formal functional calculus
powerful set of techniques and it differs from both symbolic acquiresnewandpressingrelevanceinlightoftheneuralfunc-
differentiation,asfacilitatedbycomputeralgebrasystems,and tional concepts of [41], which allow to work explicitly with
fromnumericaldifferentiationviafinitedifference,asiscom- both functional derivatives and functional integrals, which
putationalbreadandbutter.Asshowninthetutorial[42]only canbeevaluatedefficientlyviathecorrespondingstandalone
high-levelcodeisrequiredtoinvokeautomaticdifferentiation, neuralfunctionals.
and both neural and analytical functionals can be differenti- In light of these benefits it is fortunate that the func-
ated with little effort. As the derivative (of the functional) is tionaldifferentiation-integrationstructureextendsrecursively
with respect to its entire input data, the method constitutes a tohigherordersofcorrelationfunctions.Thenextlevelbeyond
representationofagenuinefunctionalderivative. equations(9)and(10)involvesthetwo-bodydirectcorrelation
Wegiveanoverview.Inthepresentcontextthefunctional functionalc 2 (r,r ′,[ρ])andtheintegrationanddifferentiation
calculusthatrelatestheone-bodydirectcorrelationstothepar- structureisasfollows:
ent excess free energy functional is given by the following ˆ ˆ
1
functionalintegrationandfunctionaldifferentiationrelations: c (r,[ρ])= dr ′ ρ(r ′ ) dac (r,r ′ ,[ρ ]), (11)
1 2 a
ˆ ˆ 0
βF exc [ρ]=− drρ(r) 0 1 dac 1 (r,[ρ a ]), (9) c 2 (r,r ′ ,[ρ])= δc δ 1 ρ ( ( r r ,[ ′ ρ ) ]) , (12)
δβF [ρ]
c (r,[ρ])=− exc . (10)
1 δρ(r) andwereferto[8,9,101,102]forbackground.
Wecanchainthefunctionalderivativestogetherbyinsert-
In equat´ion (9) we have parameterized the general formal ingc
1
(r,[ρ])asgivenbyequation(10)intothedefinition(12)
integral D[ρ]byusingρ (r)asascaledversionofthedensity of c (r,r ′,[ρ]). In parallel, we can also chain the functional
a 2
6

| J.Phys.:Condens.Matter36(2024)243002 |     |     |     |     |     |     |     |     |     |     |     |     |     | TopicalReview |     |
| ------------------------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ------------- | --- |
integralsinequations(9)and(11).Theseproceduresyieldthe we have Ω =− k TlnΞ with the grand ensemble partition
0 B
−β(H−µN).Wehaveusedthesubscript0todenote
| following | second | order | functional |     | integration |     | and differenti- | sumΞ =Tre |     |     |     |     |     |     |     |
| --------- | ------ | ----- | ---------- | --- | ----------- | --- | --------------- | --------- | --- | --- | --- | --- | --- | --- | --- |
ationrelationships: equilibriumbutwedropthiselsewhereinourpresentationto
|     |     |     | ˆ   |     | ˆ   |     |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
simplifynotation.
[ρ]=− ′ ′ Inserting equation (15) into equation (16) and using the
|     | βF  | exc | drρ(r) |     | dr ρ(r | )   |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | ------ | --- | ------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
explicitformoftheidealfreeenergyfunctionaltogetherwith
|     |     |     | ˆ   | ˆ   |     |     |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
1 a the definition (10) of c (r,[ρ]) leads to equation (5) with the
|     |     |     | ×   | da  | da ′ c (r,r | ′ ,[ρ | a′]), (13) |                       |     |     | 1                                   |     |     |     |     |
| --- | --- | --- | --- | --- | ----------- | ----- | ---------- | --------------------- | --- | --- | ----------------------------------- | --- | --- | --- | --- |
|     |     |     |     |     | 2           |       |            | one-bodydirectcorrela |     |     | tionsexpressedasadensityfunctional, |     |     |     |     |
|     |     |     | 0   | 0   |             |       |            |                       |     |     |                                     |     |     |     |     |
δ2βF as anticipated in section 1.2. Exponentiating and regrouping
|     |     | ′ ,[ρ])=− |     | exc [ρ] |     |     |     |     |     |     |     |     |     |     |     |
| --- | --- | --------- | --- | ------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
c (r,r , (14) thetermsthenyieldsthefollowingpopularformoftheEuler–
|     | 2   |     | δρ(r)δρ(r |     | ′)  |     |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | --------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Lagrangeequation:
where the scaled density profile in equation (13) is ρ a′(r)= ρ(r)=exp(−βV
′ρ(r).Thedoubleparameterintegralinequation(13)canbe (r)+βµ+c (r,[ρ])). (18)
| a   |     |     |     |     |     |     |     |     |     |     | ext |     | 1   |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
further simplified [7], as described at the end of section 3.4. Equation(18)isaself-consistencyrelationthatcanbesolved
The generalization of equation (14) to the n-th functional ρ(r)
|            |     |             |        |        |             |     |             | efficiently  | for the | equilibrium |       | density    | profile |        | via iterat- |
| ---------- | --- | ----------- | ------ | ------ | ----------- | --- | ----------- | ------------ | ------- | ----------- | ----- | ---------- | ------- | ------ | ----------- |
| derivative |     | defines the | n-body | direct | correlation |     | functional, |              |         |             |       |            |         |        |             |
|            |     |             |        |        |             |     |             | ive methods, | as      | detailed    | below | in section |         | 2.3. A | prerequis-  |
which remains functionally dependent on the density pro- ite is that c (r,[ρ]) is known, usually as an approximation
1
| file | and which | possesses |     | spatial | dependence |     | on n position |         |          |      |                |     |        |      |        |
| ---- | --------- | --------- | --- | ------- | ---------- | --- | ------------- | ------- | -------- | ---- | -------------- | --- | ------ | ---- | ------ |
|      |           |           |     |         |            |     |               | that is | obtained | from | an approximate |     | excess | free | energy |
arguments.Althoughincreasingnyieldsobjectsthatbecome functional F [ρ] via functionally differentiating according
exc
| very | rapidly | out of | any practical |     | reach, | the neural | functional |             |       |        |          |     |             |          |     |
| ---- | ------- | ------ | ------------- | --- | ------ | ---------- | ---------- | ----------- | ----- | ------ | -------- | --- | ----------- | -------- | --- |
|      |         |        |               |     |        |            |            | to equation | (10). | Having | obtained |     | a numerical | solution | of  |
conceptprovidesmuchfuelformakingprogress.Whilewedo
equation(18)forthedensityprofile,thiscanthenbeinserted
|     |     | ′,r | ′′,[ρ])here,Sammülleretalhavedemon- |     |     |     |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | ----------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
notcoverc (r,r intothegrandpotentialfunctional(15)toobtainfullthermo-
3
| strated | its | general accessiblity |     | and | physical | validity | for bulk |     |     |     |     |     |     |     |     |
| ------- | --- | -------------------- | --- | --- | -------- | -------- | -------- | --- | --- | --- | --- | --- | --- | --- | --- |
dynamicinformationviaequation(17),whichbyconstruction
| fluidsin[41].               |      |                |     |        |                            |     |                  | isconsistentwiththedensityprofile.                  |     |     |               |     |          |           |       |
| --------------------------- | ---- | -------------- | --- | ------ | -------------------------- | --- | ---------------- | --------------------------------------------------- | --- | --- | ------------- | --- | -------- | --------- | ----- |
| We                          | have | so far focused |     | on the | properties                 |     | of the intrinsic |                                                     |     |     |               |     |          |           |       |
|                             |      |                |     |        |                            |     |                  | We demonstrate                                      |     | in  | the following |     | how this | classical | func- |
| excessfreeenergyfunctionalF |      |                |     |        | [ρ]anditsdensityfunctional |     |                  |                                                     |     |     |               |     |          |           |       |
|                             |      |                |     | exc    |                            |     |                  | tionalbackgroundcanbeputtoformidableuseviahybridiz- |     |     |               |     |          |           |       |
derivatives.ThisisnaturalasclassicallyF [ρ]isthecentral ation with simulation-based machine learning. As our aim is
exc
objectthatcontainstheeffectsoftheinterparticleinteractions
pedagogical,wechoosetheone-dimensionalhardcoresystem
andthusdependsinanontrivialwayonitsinputdensitypro- asaconcreteexampletodemonstratethegeneralmethodology
| file. | The functional |     | F [ρ] | is intrinsic |     | in the | sense that it | is  |     |     |     |     |     |     |     |
| ----- | -------------- | --- | ----- | ------------ | --- | ------ | ------------- | --- | --- | --- | --- | --- | --- | --- | --- |
exc [41]. We complement the neural functional structure with a
independentofexternalinfluence.Werecallthatweherework
|     |     |     |     |     |     |     |     | description | of Percus’ |     | analytical | solution, | which | then | allows |
| --- | --- | --- | --- | --- | --- | --- | --- | ----------- | ---------- | --- | ---------- | --------- | ----- | ---- | ------ |
inthegrandensemble(seee.g.[103–106]forstudiesaddress- formirroringoftheneuraltheory.
| ing the         | canonical | ensemble      |     | of fixed  | particle | number). | Hence        |     |     |     |     |     |     |     |     |
| --------------- | --------- | ------------- | --- | --------- | -------- | -------- | ------------ | --- | --- | --- | --- | --- | --- | --- | --- |
| the appropriate |           | thermodynamic |     | potential |          | is the   | grand canon- |     |     |     |     |     |     |     |     |
2. Neuralfunctionaltheory
icalfreeenergyorgrandpotential.Thisisrequiredinorderto
determineρ(r).
|     |     |     |     |     |     |     |     | Jerry Percus | famously |     | wrote | in the abstract |     | of his | 1976 stat- |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------ | -------- | --- | ----- | --------------- | --- | ------ | ---------- |
Whenexpressedasadensityfunctionalthegrandpotential
|          |     |               |     |     |        |         |               | istical mechanics |     | landmark |     | paper [55]: | ‘The | external | field |
| -------- | --- | ------------- | --- | --- | ------ | ------- | ------------- | ----------------- | --- | -------- | --- | ----------- | ---- | -------- | ----- |
| consists | of  | the following | sum | of  | ideal, | excess, | external, and |                   |     |          |     |             |      |          |       |
requiredtoproduceagivendensitypatternisobtainedexpli-
chemicalpotentialcontributions:
|     |     |     |     |     |     |     |     | citly for | a classical | fluid | of  | hard rods. | All | direct correlation |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --------- | ----------- | ----- | --- | ---------- | --- | ------------------ | --- |
ˆ
|        |     |       |      |          |     | (r)−µ]. |      | functions | are shown | to  | be of | finite range | in  | all pairs | of vari- |
| ------ | --- | ----- | ---- | -------- | --- | ------- | ---- | --------- | --------- | --- | ----- | ------------ | --- | --------- | -------- |
| Ω[ρ]=F |     | [ρ]+F | [ρ]+ | drρ(r)[V |     |         | (15) |           |           |     |       |              |     |           |          |
id exc ext ables.’Herewerelatehisachievementtotheneuralfunctional
|     |     |     |     |     |     |     |     | theory, | which allows |     | to reproduce | numerically |     | a   | variety of |
| --- | --- | --- | --- | --- | --- | --- | --- | ------- | ------------ | --- | ------------ | ----------- | --- | --- | ---------- |
The form of the ideal g´as free energy functional is explicitly propertiesoftheexactsolution.Weemphasizethattheneural
drρ(r)[lnρ(r)−
knownasF [ρ]=k T 1]andthethirdterm functional theory remains generic in its applicability to fur-
|             |     | id            | B   |         |     |              |           |            |         |     |                   |     |             |     |         |
| ----------- | --- | ------------- | --- | ------- | --- | ------------ | --------- | ---------- | ------- | --- | ----------------- | --- | ----------- | --- | ------- |
| in equation |     | (15) contains | the | effects | of  | the external | potential |            |         |     |                   |     |             |     |         |
|             |     |               |     |         |     |              |           | ther model | fluids; | see | the supplementary |     | information |     | of [41] |
V ext (r)andoftheparticlebathatchemicalpotentialµ. forthesuccessfultreatmentofthesupercriticalLennard–Jones
The variational principle of classical density functional fluidinthreedimensions.WerefertheReadertotheprovided
theory[4,5,105]ascertainsthat onlineresources[42]foraprogrammingtutorialonthecon-
(cid:12) creteapplicationofthefollowingconcepts.Figure4showsa
δΩ[ρ](cid:12)
(cid:12) =0 (min), (16) schematicoftheworkflowthatisinherentintheneuralfunc-
δρ(r)
|     |     |     | ρ=ρ | 0   |     |     |      | tionalconcept,asdescribedinthefollowing. |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | ---- | ---------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
|     |     |     | Ω[ρ | ]=Ω | .   |     |      |                                          |     |     |     |     |     |     |     |
|     |     |     |     | 0   | 0   |     | (17) |                                          |     |     |     |     |     |     |     |
2.1. Trainingtheneuralcorrelationfunctional
| Equations |     | (16) and | (17) | imply | that | the grand | potential |     |     |     |     |     |     |     |     |
| --------- | --- | -------- | ---- | ----- | ---- | --------- | --------- | --- | --- | --- | --- | --- | --- | --- | --- |
becomesminimalatρ (r),whichisthereal,physicallyreal- TheclassicalfluidofhardrodsthatPercusconsidershasone-
0
ized density profile and Ω is the equilibrium value of the dimensional position coordinates x, with particle index i =
|     |     |     |     | 0   |     |     |     |     |     |     |     | i   |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
grand potential. Recall that based on the many-body picture 1,...,Nandapairwiseinterparticleinteractionpotentialϕ(x)
7

| J.Phys.:Condens.Matter36(2024)243002 |     |     |     |     |     |     |     |     |     | TopicalReview |     |
| ------------------------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | ------------- | --- |
furtherbelow,afterfirstlayingoutthegeneralmachinelearn-
ingstrategyof[41].Thisneuralfunctionalmethodisneither
|     |     |     |     | restricted | to hard | cores | nor to | one-dimensional |     | systems, | but |
| --- | --- | --- | --- | ---------- | ------- | ----- | ------ | --------------- | --- | -------- | --- |
addressingthiscasehereisusefultohighlightthesalientfea-
turesoftheapproach.
Weaimforexplicitlysamplingthemicrostatesofthesys-
|     |     |     |     | tem according      |           | to their     | probability | distribution   |                | via            | particle- |
| --- | --- | --- | --- | ------------------ | --------- | ------------ | ----------- | -------------- | -------------- | -------------- | --------- |
|     |     |     |     | based simulations. |           | This         | can be      | implemented    |                | efficiently,   | and       |
|     |     |     |     | for the            | present   | introductory |             | purposes       | in also        | an intuitively |           |
|     |     |     |     | accessible         | way,      | via grand    | canonical   |                | Monte          | Carlo (GCMC)   |           |
|     |     |     |     | sampling.          | Excellent | accounts     |             | of this method |                | are given      | in [8,    |
|     |     |     |     | 107–109].          | Briefly,  | a Markov     |             | chain          | of microstates |                | is con-   |
|     |     |     |     | structed,          | where     | based        | on a given  | configuration, |                | a trial        | step      |
|     |     |     |     | is proposed,       | which     | is           | accepted    | with           | a probability  | given          | by        |
|     |     |     |     | a Metropolis       | function  |              | involving   | the            | energy         | difference     | ∆E        |
betweentheoriginalandthetrialstate.
|     |     |     |     | Three | trial | moves are | used | in the | simplest | yet powerful |     |
| --- | --- | --- | --- | ----- | ----- | --------- | ---- | ------ | -------- | ------------ | --- |
Figure4. Schematicoftheworkflowoftheneuralfunctional
scheme:(i)Selectingoneparticleirandomlyanddisplacingit
theory.Many-bodysimulationsunderrandomizedconditionsare
usedtosamplestatisticallyaveragedandspatiallyresolveddatathat uniformlywithinagivenmaximalcutoffdistance.Ifthedis-
characterizetheinhomogeneousresponseoftheconsideredsystem. placement creates overlap, then the trial move is discarded.
Aneuralnetworkisthentrainedtorepresentthedirectcorrelation Ifotherwisethereisnooverlapinthenewconfiguration,the
functional,whichissubsequentlyappliednumericallyandvia
energydifferenceisduetoonlytheexternalpotential,∆E=
| neuralfunctionalmethodstoinvestigatethephysicsofthesystemin |     |     |     | ′)−   |                                            |     |     |     |     |     |     |
| ----------------------------------------------------------- | --- | --- | --- | ----- | ------------------------------------------ | --- | --- | --- | --- | --- | --- |
|                                                             |     |     |     | V (x  | V (x),wheretheprimedenotesthetrialposition |     |     |     |     |     |     |
| thedesiredtargetsituations.                                 |     |     |     | ext i | ext                                        | i   |     |     |     |     |     |
ofparticlei.(ii)Anewparticlejisinsertedatarandomposi-
tionx withenergychangethataccountsforboththeexternal
j
|     |     |     |     | potential | and the | chemical | equilibrium |     | with the | particle | bath |
| --- | --- | --- | --- | --------- | ------- | -------- | ----------- | --- | -------- | -------- | ---- |
whichisinfiniteifthedistancexbetweenthetwoparticlesis
′)−µ.
smallerthantheirdiameter,x<σ,anditvanishesotherwise. and hence ∆E=V (x (iii) Correspondingly, a ran-
|                                          |     |     |           |                |     | ext      | j            |     |          |         |     |
| ---------------------------------------- | --- | --- | --------- | -------------- | --- | -------- | ------------ | --- | -------- | ------- | --- |
|                                          |     |     |           | domly selected |     | particle | i is removed |     | from the | system. | The |
| ThesystemisexposedtoanexternalpotentialV |     |     | (x),which |                |     |          |              |     |          |         |     |
ext
isafunctionofpositionxacrossthesystem,andthisingeneral acceptance of the removal happens again with a probabil-
createsaninhomogeneous‘densitypattern’ρ(x). ity given by the Metropolis function with energy difference
|                                                       |     |     |     | ∆E=− | V (x)+µ. |     |     |     |     |     |     |
| ----------------------------------------------------- | --- | --- | --- | ---- | -------- | --- | --- | --- | --- | --- | --- |
| Weadjustthedefinition(1)ofthedensitydistributiontothe |     |     |     |      | ext i    |     |     |     |     |     |     |
presentone-dimensionalcase: Despite its conceptual simplicity GCMC is a very power-
fulmethodfortheinvestigationofcomplexeffects[107–109]
|     | DX  | E   |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
andsignificantextensionsexistbothintheformofhistogram
|     | ρ(x)= | δ(x − ) , |      |                                                    |     |     |     |     |     |     |     |
| --- | ----- | --------- | ---- | -------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
|     |       | x i       | (19) | techniques[108,109]andthetailoringofmorecomplexand |     |     |     |     |     |     |     |
i collective trial moves. Investigating a typical physical prob-
lem,asspecifiedbytheinterparticleinteractionsu(rN)andthe
whereδ(·)hereindicatestheDiracdistributioninonedimen- typeofconsideredexternalinfluence,suchaswallsasrepres-
(r),requirese.g.scanningofthe
sionandthebracketsindicateagrandcanonicalthermalaver- entedbyamodelformofV ext
age. Due to the hard core nature of the model, the statistical thermodynamic parameters and acquiring good enough stat-
weightofeach‘alPlowed’microstateisparticularlysimpleand istics at each statepoint. Our ultimate goal (section 2.3) is to
givenbyexp[−β
V (x)+βµN]/Ξ,whereΞisanormal- perform this tasks with significant gain in efficiency via the
i ext i
izingfactor.Allowedmicrostatesarethoseforwhichalldis- neuraltheory;were-iteratetheavailabilityvia[42]ofhands-
| − |⩾σ.
tinctparticlepairsijarespacedfarenoughapart, x i x j oncodeexamplesforthepresenthardrodmodel.
Ifalreadyasingleoverlapoccurs,thenthemicrostateis‘for- Webasethetrainingonthefollowingrewritingandadapta-
bidden’astheinterparticlepotentialbecomesformallyinfin- tionofthechemicalpotentialbalanceequation(5)totheone-
ite,whichthencreatesvanishingstatisticalweight;werecall dimensionalsystem:
theillustrationinfigure1.
|     |     |     |     |     |     | (x)=lnρ(x)+βV |     |     | (x)−βµ. |     |     |
| --- | --- | --- | --- | --- | --- | ------------- | --- | --- | ------- | --- | --- |
Despite the apparent simplicity of the many-body prob- c 1 ext (20)
| ability distribution, | the Statistical | Mechanics | of the hard rod |     |     |     |     |     |     |     |     |
| --------------------- | --------------- | --------- | --------------- | --- | --- | --- | --- | --- | --- | --- | --- |
model is nontrivial. The particles interact nonlocally over Allquantitiesontherighthandsideareeitherprescribedapri-
the lengthscale σ and the external potential has no restric- oriorareaccessibleviatheGCMCsimulations:Specifically,
tionsonitsshapeoronthelengthscale(s)ofvariation.Hence the density profile ρ(x) is obtained by filling a position-
features such as jumps and positive infinities that represent resolved histogram according to the encountered microstates
hard walls are allowed. In bulk, V (x)=0, and the solu- asspecifiedbyitsparticlecoordinatesx.Werecalltheformal
|     |     | ext |     |     |     |     |     |     | i   |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
tion is straightforward [8, 54]. The general case is however definition(19)ofρ(x)viatheDiracdistribution,whichinprac-
highlynontrivial,whichmakesPercus’abovequotedopening ticeisdiscretizedsuchthatsufficientfinitespatialresolution,
a very remarkable one. We present more details of his work say0.01σ,isobtained.This‘counting’methodisarguablythe
8

| J.Phys.:Condens.Matter36(2024)243002 |     |     |     |     |           |      |            |     |      |        |          | TopicalReview |
| ------------------------------------ | --- | --- | --- | --- | --------- | ---- | ---------- | --- | ---- | ------ | -------- | ------------- |
|                                      |     |     |     |     | different | GCMC | simulation |     | runs | and in | practice | we per-       |
form512ofthese.Theresultisasetofcorrespondingdens-
|     |     |     |     |     | ity profiles | ρ(k)(x). | We  | then | use equation |     | (20) | to obtain for |
| --- | --- | --- | --- | --- | ------------ | -------- | --- | ---- | ------------ | --- | ---- | ------------- |
eachruntheone-bodydirectcorrelationprofilesfromsimply
|     |     |     |     |     | addingup:c | (k)(x)=lnρ(k)(x)+βV |          |         |                           | (k)(x)−βµ(k).Asaresult |     |               |
| --- | --- | --- | --- | --- | ---------- | ------------------- | -------- | ------- | ------------------------- | ---------------------- | --- | ------------- |
|     |     |     |     |     |            | 1                   |          |         |                           | ext                    |     |               |
|     |     |     |     |     | of the     | simulation          | protocol | we      | have                      | generated              | a   | bare data set |
|     |     |     |     |     | {βµ(k),βV  | (k)(x),ρ(k)(x),c    |          | (k)(x)} | forallpositionsxandforall |                        |     |               |
|     |     |     |     |     |            | ext                 |          | 1       |                           |                        |     |               |
differentrunsk.Asapracticaldetail,thisrequirestoexclude
|     |     |     |     |     | regionswhereρ(x)=0andV |     |     |     | (x)=∞ | .   |     |     |
| --- | --- | --- | --- | --- | ---------------------- | --- | --- | --- | ----- | --- | --- | --- |
ext
Inordertoaddressourdeclaredgoaltolearnafunctional
|     |     |     |     |     | dependenceofc |     | (x),wehavetocarveoutanontrivialdepend- |     |     |     |     |     |
| --- | --- | --- | --- | --- | ------------- | --- | -------------------------------------- | --- | --- | --- | --- | --- |
1
encerelationshipandhencerestrictthedatainput.Motivated
|     |     |     |     |     | by the                                | physics, | one might | see | the | scaled | chemical          | potential |
| --- | --- | --- | --- | --- | ------------------------------------- | -------- | --------- | --- | --- | ------ | ----------------- | --------- |
|     |     |     |     |     | βµ(k) andthescaledexternalpotentialβV |          |           |     |     |        | (k)(x)tobethetrue |           |
ext
mechanicaloriginoftheshapeofthedirectcorrelationfunc-
(k)(x).
|     |     |     |     |     | tion c | However, |     | the insights |     | provided | by density | func- |
| --- | --- | --- | --- | --- | ------ | -------- | --- | ------------ | --- | -------- | ---------- | ----- |
1
Figure5. Illustrationoftheneuralone-bodydirectcorrelation tional theory hint at the fact that this is not the best possible
| functionalc (x,[ρ])representedbyafullyconnectedneuralnetwork |     |     |     |     |                                           |     |     |     |     |     |     |     |
| ------------------------------------------------------------ | --- | --- | --- | --- | ----------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
| 1                                                            |     |     |     |     | choiceoffunctionalrelationshiptoconsider. |     |     |     |     |     |     |     |
withthreehiddenlayers.Thetopologymapsasmallfinitewindow
|     |     |     |     |     | We  | recapitulate | that | the | GCMC | simulations |     | yield data |
| --- | --- | --- | --- | --- | --- | ------------ | ---- | --- | ---- | ----------- | --- | ---------- |
ofthedensityprofileρ(x)tothelocalvalueofthedirectcorrelation
accordingto:
functionc (x).
1
|     |     |     |     |     |     | n   |                | o   |     | n       | o   |        |
| --- | --- | --- | --- | --- | --- | --- | -------------- | --- | --- | ------- | --- | ------ |
|     |     |     |     |     |     |     |                |     | L   |         | L   |        |
|     |     |     |     |     |     |     | (k)(x ′ )−µ(k) |     | −→  | ρ(k)(x) |     |        |
|     |     |     |     |     |     |     | V              |     |     |         |     | , (21) |
ext
most intuitive one to obtain data for the density profile. As 0 0
anaside,thereisanumberofforce-samplingtechniquesthat
|     |     |     |     |     | where | the curly | brackets | indicate |     | all function | values | inside |
| --- | --- | --- | --- | --- | ----- | --------- | -------- | -------- | --- | ------------ | ------ | ------ |
canimprovethestatisticalvariancesignificantly[97,110–112] of the system box, with ranges 0 ⩽ x ′⩽ L and 0 ⩽ x ⩽ L;
andthatalsocanservetogaugethequalityofsamplingofthe
|     |     |     |     |     | the arrow | indicates | an  | input-output |     | relationship. |     | Applying |
| --- | --- | --- | --- | --- | --------- | --------- | --- | ------------ | --- | ------------- | --- | -------- |
equilibriumensemble[97]. equation(20)totheentiredatasetalsoallowstohavethedirect
| While the | issues of Monte | Carlo | sampling efficiency | and |     |     |     |     |     |     |     |     |
| --------- | --------------- | ----- | ------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
correlationfunctionasanoutputaccordingto:
| quality assessment | of thermal | averages | can be pertinent |     | in  |     |     |     |     |     |     |     |
| ------------------ | ---------- | -------- | ---------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|                    |            |          |                  |     |     | n   |     | o   |     | n   | o   |     |
higherdimensionsandinphysicallymorecomplexsituations, (k)(x ′ L (k)(x) L
|                                                       |           |             |                     |     |     |     | V )−µ(k) |     | −→  | c   |     | . (22) |
| ----------------------------------------------------- | --------- | ----------- | ------------------- | --- | --- | --- | -------- | --- | --- | --- | --- | ------ |
| thesimplicityofthepresentone-dimensionalhardcoremodel |           |             |                     |     |     |     | ext      |     |     | 1   |     |        |
|                                                       |           |             |                     |     |     |     |          |     | 0   |     | 0   |        |
| makes counting                                        | according | to equation | (19) an appropriate |     |     |     |          |     |     |     |     |        |
Ifoneweretomimicthesimulationsdirectlybytheneuralnet-
choicetoobtaindataforρ(x).Thenaddingupthethreecon-
tributionsontherighthandsideofequation(20)yieldsresults workonewouldbetemptedtobasethetrainingdirectlyupon
equation(22).Inlessclearcutmachine-learningsituationsthan
forc (x).Weproceedatthisdata-generationstagesomewhat
1
hereticallyandignoreatfirstthecentralrolethatc (x)plays considered here, it can be a standard strategy to attempt to
1
representthecausalrelationship,whichgovernsthecomplex
forthephysicsofinhomogeneoussystems.
mathematicalorreal-worldsystemunderconsideration,bya
| In contrast | to the typical | deterministic | setup for investig- |     |     |     |     |     |     |     |     |     |
| ----------- | -------------- | ------------- | ------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
ating a specific physical situation described above, training surrogateartificialintelligencemodel.Thepresentfunctional
formulationofStatisticalMechanicshintsatpotentialcaveats,
theneuralnetworkproceedsonthebasisofrandomizedsitu-
ations rather than with the ultimate application in mind; we suchasthenecessityofdealingwiththefullinputandoutput
′
datasets(parameterrangesofxandx)acrosstheentiresys-
recalltheillustrationoftheneuralfunctionalworkflowshown
tem.Furthermorethespecificphysicsofthemutuallyinteract-
infigure4.Themotivationforusingthisstrategycomesfrom
thegoalofcapturingviathemachinelearningtheintrinsicdir- ingrodsappearstoplaynorole.
|     |     |     |     |     | The | density | functional-inspired |     |     | training | (section | 1.2) pro- |
| --- | --- | --- | --- | --- | --- | ------- | ------------------- | --- | --- | -------- | -------- | --------- |
ectcorrelationsofthemany-bodysystemthatthentranscend
thespecificinhomogeneoussituationsthatwereunderconsid- ceeds very differently. We here take a pragmatic stance and
|     |     |     |     |     | attempt | to create | via | training | a neural | representation |     | of the |
| --- | --- | --- | --- | --- | ------- | --------- | --- | -------- | -------- | -------------- | --- | ------ |
erationduringtraining.Figure5depictsanillustrationofthe
|                                                       |     |     |     |     | dependence | of  | c (x) on | ρ(x) | alone. | This leads | to  | a surrogate |
| ----------------------------------------------------- | --- | --- | --- | --- | ---------- | --- | -------- | ---- | ------ | ---------- | --- | ----------- |
| neuralnetworktopologyofthetrainedcentralneuralnetwork |     |     |     |     |            |     | 1        |      |        |            |     |             |
(x,[ρ])basedonthefollowingmapping
| c (x,[ρ])anditsrelationtothephysicalinputandoutputquant- |      |     |     |     | modelc |     |     |        |     |     |     |     |
| -------------------------------------------------------- | ---- | --- | --- | --- | ------ | --- | --- | ------ | --- | --- | --- | --- |
| 1                                                        |      |     |     |     |        | 1   |     |        |     |     |     |     |
|                                                          |      |     |     |     |        |     | n   | o      |     |     |     |     |
| ities,i.e.toρ(x)andc                                     | (x). |     |     |     |        |     |     |        |     |     |     |     |
|                                                          | 1    |     |     |     |        |     |     | ′ x+xc |     |     |     |     |
We hence perform a sequence of simulation runs, where ρ(k)(x ) −→ c (k)(x), (23)
1
| eachrunhasaninputvalueβµ(k)andaninputfunctionalshape |     |     |     |     |     |     |     | x−xc |     |     |     |     |
| ---------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | ---- | --- | --- | --- | --- |
βV ( k) (x),bothofwhicharegeneratedrandomly.Specifically,
| ex t |     |     |     |     | wheretheinputonthelefthandsideconsistsoffunctionval- |     |     |     |     |     |     |     |
| ---- | --- | --- | --- | --- | ---------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
′)
we combine sinusoidal functions with periodicities that are ues ρ(k)(x that lie inside the density window centered at x,
commensurate with the box length L, linear discontinuous i.e.onlythevaluesx ′ thatliewithinanarrowintervalx − x ⩽
c
|     |     |     | (k)(x); |     | ′⩽  |     |     |     |     |     |     |     |
| --- | --- | --- | ------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
segments, and hard walls in the creation of V see [41, x x+x .Herex isacutoffparameterthatforshort-ranged
|     |     |     | ext |     |     | c   | c   |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
42] for further details. The superscript k enumerates the interparticlepotentialsisoftheorderoftheparticlesize.For
9

| J.Phys.:Condens.Matter36(2024)243002 |     |     |     |     |     |     |     |     |     |     |     |     | TopicalReview |
| ------------------------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ------------- |
thepresentone-dimensionalhardcoresystemwesetx =σ. as one would expect from the fact that the rods interact over
c
Insteadofhavingtooutputanentirefunction,aswouldbethe the finite distance σ, and it is also nonlinear, as is consist-
casewhenattemptingtolearnviaequation(22),heretheout- entwiththebehaviourofanontriviallyinteractingmany-body
putismerelythesinglevalueofthedirectcorrelationfunction system. The spatial dependence is characterized by convolu-
atthecenterofthedensitywindow.Werecallthatthistarget tionoperationswhich,despiteperformingthetaskofcoarse-
value is obtained from the simulation data via equation (20) graining, retain the full character of the microscopic interac-
|     | (k)(x)=lnρ(k)(x)+βV |     |     | (k)(x)−βµ(k) |     |     |     |     |     |     |     |     |     |
| --- | ------------------- | --- | --- | ------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- |
such that c for each run tions.ThePercusfunctionalprovidedmotivationfordevelop-
|     | 1   |     |     | ext |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
ingso-calledweighted-densityapproximations[8],wherethe
| k. A simple | GCMC | code is | provided | online | [42], along | with |     |     |     |     |     |     |     |
| ----------- | ---- | ------- | -------- | ------ | ----------- | ---- | --- | --- | --- | --- | --- | --- | --- |
a pre-generated simulation data set and a pre-trained neural densityprofileisconvolvedwithoneorseveralweightfunc-
functional. tionsthatarethenfurtherprocessedtogivetheultimatevalue
ofthedensityfunctional.
| We choose |     | the loss function | to  | be the mean | squared | error |     |     |     |     |     |     |     |
| --------- | --- | ----------------- | --- | ----------- | ------- | ----- | --- | --- | --- | --- | --- | --- | --- |
oftheneuralnetworkoutputcomparedtothesimulationref- We here give the Percus direct correlation functional in
(x),asobtainedviaequation(20).Asafur- Rosenfeld’sgeometry-basedfundamentalmeasurerepresent-
| erencevalueforc |     | 1   |     |     |     |     |     |     |     |     |     |     |     |
| --------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
thermetrictogaugethetrainingprogress,wemakeuseofthe ation, see [59] for a historical perspective. Instead of work-
meanabsoluteerrorofreferenceandoutput.Bothchoicesare ing with the particle diameter σ as the fundamental length-
|     |     |     |     |     |     |     | scale, Rosenfeld |     | rather | bases | his description | on  | the particle |
| --- | --- | --- | --- | --- | --- | --- | ---------------- | --- | ------ | ----- | --------------- | --- | ------------ |
standard[100].Thequadraticlossisconvenientasitisanalyt-
ical and hence the machine-learning gradient-based methods radius R=σ/2, which allows to find deep geometric mean-
|          |        |          |          |          |               |     | ing in Percus’ |     | expressions | and | to also generalize |     | to higher |
| -------- | ------ | -------- | -------- | -------- | ------------- | --- | -------------- | --- | ----------- | --- | ------------------ | --- | --------- |
| directly | apply. | The mean | absolute | error is | nonanalytical | due |                |     |             |     |                    |     |           |
tothemodulusinvolved,butitisausefulsupportingquantity dimensions[60,61,65].
thathasaverydirectinterpretation. Theexactform[60]oftheone-bodydirectcorrelationfunc-
tionalisanalyticallygivenasthefollowingsum:
| After | training | the mean | absolute | error | was of | the order |     |     |     |     |     |     |     |
| ----- | -------- | -------- | -------- | ----- | ------ | --------- | --- | --- | --- | --- | --- | --- | --- |
of ∼ 0.013, which implies that the neural network prediction ˆ
|     |     |     |     |     |     |     |     |     | −    |      |       | x+R |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ---- | ---- | ----- | --- | --- |
|     |     |     |     |     |     |     |     |     | Φ (x | R)+Φ | (x+R) |     |     |
deviates on average by this value from the simulation data. c (x,[ρ])=− 0 0 − dx ′ Φ (x ′ ).
|     |     |     |     |     |     |     | 1   |     |     |     |     |     | 1   |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
Although the simulation data carries some statistical noise, 2 x−R
| itseffectiscomparativelysmaller,whentakingthenumerical |     |     |     |     |     |     |     |     |     |     |     |     | (24) |
| ------------------------------------------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---- |
solutionofthePercustheory(detailedbelow)asthereference.
Our training data consists of 512 simulation runs using a HerethetwofunctionsΦ (x)andΦ (x)eachdependontwo
|                                                      |      |             |         |             |             |      |                    |     |         | 0    | 1                      |     |      |
| ---------------------------------------------------- | ---- | ----------- | ------- | ----------- | ----------- | ---- | ------------------ | --- | ------- | ---- | ---------------------- | --- | ---- |
|                                                      |      | L=10σ.      |         |             |             |      | weighteddensitiesn |     | (x)andn |      | (x)inthefollowingform: |     |      |
| simulation                                           | box  | size of     |         | Each of the | simulation  | runs |                    |     | 0       |      | 1                      |     |      |
| requires                                             | only | about three | minutes | runtime     | on a single | CPU  |                    |     |         |      |                        |     |      |
|                                                      |      |             |         |             |             |      |                    |     | (x)=−   |      | −                      |     |      |
| coreofastandarddesktopmachine.                       |      |             |         |             |             |      |                    |     | Φ 0     | ln[1 | n 1 (x)],              |     | (25) |
| Weuseastandardfully-connectedartificialneuralnetwork |      |             |         |             |             |      |                    |     |         | n    | 0 (x)                  |     |      |
|                                                      |      |             |         |             |             |      |                    |     | Φ (x)=  |      | .                      |     | (26) |
with three hidden layers that respectively possess 128, 64 1 1 − n (x)
1
and32nodes.Weuse201inputnodestorepresentthedens-
ity profile in a finite window of size 1σ and spatial bin size Theweighteddensitiesn (x)andn (x)areobtainedfromthe
|     |     |     |     |     |     |     |     |     |     | 0   | 1   |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
0.01σ, where we recall that σ is the particle size. To accom- baredensityprofileviaspatialaveraging:
| modate | the local | functional | mapping, | we  | reshape | the train- |     |     |     |       |           |     |     |
| ------ | --------- | ---------- | -------- | --- | ------- | ---------- | --- | --- | --- | ----- | --------- | --- | --- |
|        |           |            |          |     |         |            |     |     |     | ρ(x − | R)+ρ(x+R) |     |     |
ingdataintoinputdensitywindowsandcorrespondingoutput
|           |      |          |            |         |      |          |     |     | n (x)= |     |     | ,   | (27) |
| --------- | ---- | -------- | ---------- | ------- | ---- | -------- | --- | --- | ------ | --- | --- | --- | ---- |
|           | (x), |          |            |         |      |          |     |     | 0      |     | 2   |     |      |
| values of | c 1  | where we | also apply | twofold | data | augment- |     |     |        | ˆ   |     |     |      |
x+R
ation by exploiting mirror symmetry of the simulation res- ′ ′
|                 |     |               |     |       |           |       |     |     | n (x)= |     | dx ρ(x ). |     | (28) |
| --------------- | --- | ------------- | --- | ----- | --------- | ----- | --- | --- | ------ | --- | --------- | --- | ---- |
| ults. Excluding |     | regions where | V   | (x)=∞ | and hence | where |     |     | 1      |     |           |     |      |
|                 |     |               | ext |       |           |       |     |     |        | x−R |           |     |      |
∼ 106
| equation(20)isnotdefined,thisresultsin |     |     |     |     | input-output |     |     |     |     |     |     |     |     |
| -------------------------------------- | --- | --- | --- | --- | ------------ | --- | --- | --- | --- | --- | --- | --- | --- |
±
pairs. The discrete spatial averaging at positions x R in the
|      |           |             |     |         |             |     | weighted | density | (27) | parallels | that in | the first | term of |
| ---- | --------- | ----------- | --- | ------- | ----------- | --- | -------- | ------- | ---- | --------- | ------- | --------- | ------- |
| From | the above | description | and | without | considering | the |          |         |      |           |         |           |         |
backgroundindensityfunctionaltheoryitisnotevidentthat equation (24). Similarly the position integral over the inter-
−
thetrainingwillbesuccessfulandminimizethelosssatisfact- val[x R,x+R]inequation(28)appearsanalogouslyinthe
|                              |     |     |                           |     |     |     | second term | of  | equation | (24). | These similarities |     | are not by |
| ---------------------------- | --- | --- | ------------------------- | --- | --- | --- | ----------- | --- | -------- | ----- | ------------------ | --- | ---------- |
| orilytoyieldatrainednetworkc |     |     | (x,[ρ]).Fromamathematical |     |     |     |             |     |          |       |                    |     |            |
1
pointofview,thisraisesthequestionswhetheracorrespond- coincidence.Thestructureisratherinheritedfromthegrand-
(x,[ρ])indeedexistandwhetheritisunique.And mother (excess free energy) functional, as is described in
| ingobjectc                                            | 1   |     |     |     |     |     |             |     |     |     |     |     |     |
| ----------------------------------------------------- | --- | --- | --- | --- | --- | --- | ----------- | --- | --- | --- | --- | --- | --- |
| ifso,isitsstructuresimpleenoughthatitcanbewrittendown |     |     |     |     |     |     | section3.1. |     |     |     |     |     |     |
explicitly? Having the analytical solution (24)–(28) for c (x,[ρ])
1
|                                              |     |     |     |     |     |     | allows for                             | carrying | out      | numerical | evaluation   | and              | comparing |
| -------------------------------------------- | --- | --- | --- | --- | --- | --- | -------------------------------------- | -------- | -------- | --------- | ------------ | ---------------- | --------- |
|                                              |     |     |     |     |     |     | againstresultsfromtheneuralfunctionalc |          |          |           |              | (x,[ρ]).Therange |           |
| 2.2. Percus’exactdirectcorrelationfunctional |     |     |     |     |     |     |                                        |          |          |           |              | 1                |           |
|                                              |     |     |     |     |     |     | of nonlocality,                        |          | i.e. the | distance  | across which | information      | of        |
(x,[ρ])
Due to Percus singular achievement [55] the one-body dir- the density profile enters the determination of c 1 via
ect correlation functional c (x,[ρ]) for interacting hard rods equations(24)–(28)isstrictlyfinite,asannouncedinPercus’
1
in one spatial dimension is known analytically and this has abstract [55]. As two averaging operations, each with range
±
triggeredmuchsubsequentprogress,seee.g.[56–58,60–65]. R,arechainedtogether,thecompositeprocedurehasarange
Thefunctionaldependenceonthedensityprofileisnonlocal, of ± 2R=±σ,inlinewithourtruncationofthedensityprofiles
10

J.Phys.:Condens.Matter36(2024)243002 TopicalReview
Figure6. Representativedensityprofilesthattheinhomogeneoushardrodsystemexhibitsundertheinfluenceofanexternalpotential.The
resultsareobtainedfromnumericallysolvingequation(29)uponusingeithertheneuraldirectcorrelationfunctionalc (x,[ρ])orPercus
1
exactsolutionthereof.Thethreecasescomprise(a)twohardwallswithseparationdistance9σandchemicalpotentialβµ=2,(b)twohard
wallswithmuchsmallerseparationdistance2σandidenticalchemicalpotentialβµ=2,and(c)sedimentation-diffusionequilibriumunder
gravitywithalocallyvaryingchemicalpotential,βµ
loc
(x)=βµ−βVext (x)=2−0.05x/σ;herethelinearlyvaryingcontributionaccounts
fortheinfluenceofgravityonthesystemandconfinementisprovidedbytwowidelyspacedhardwallsatx=0.5σandx=99.5σ.Notethe
crossoverinpanel(c)fromthestronglyoscillatorybehaviournearthelowerwalltoaverysmoothdensitydecay,effectivelyfollowinga
localdensityapproximation[8],uponincreasingthescaledheightx/σ.
inthetrainingdatasetsaccordingtoequation(23).Anumer- guessinthecorrectdirectiontowardtheself-consistentsolu-
icalimplementationofPercusdirectcorrelationfunctionalis tion. This is numerically fast and straightforward to imple-
availableonline[42]. ment, see the tutorial [42]. A common choice is to mix five
percentofthenewsolutiontothepriorestimate.
Aslaidoutabove,wechoosetheone-dimensionalhardcore
2.3. Applicationinsideandbeyondthebox
model due to both the availability of Percus’ functional and
Actually making the predictions for the hard rod model is the computational ease of both numerical evaluation of the
nowstraightforwardaswecanresorttodensityfunctionalthe- analytical expressions and of carrying out many-body sim-
ory and its standard use in application to physical problems. ulations. On the downside, the model does not form a very
The arguably most common method for solving the Euler– credible platform for assessing the numerical efficiency gain
Lagrangeequationself-consistentlyisbasedonequation(18), of the neural theory, as in general one will be interested in
whichwere-expressfortheone-dimensionalcaseconsidered: morecomplexsystemsandmorecomplexphysicalsituations
thanaddressedhere.Nevertheless,togivearoughideaabout
ρ(x)=exp(−βV (x)+βµ+c (x,[ρ])). (29) the required computational workload, minimizing the neural
ext 1
density functional takes of the order of seconds on a GPU,
Werecallthattherangeofnonlocalityofc (x,[ρ])islim- while the GCMC simulation runtime is of the order of sev-
1
itedtoonlytheparticlesizeσandthatwewereabletoextract eral minutes. Minimizing the analytical Percus functional is
the functional dependence from simulation data obtained by fasterthanusingtheneuralnetwork,duetothesimplestruc-
sampling in boxes of size L. Although the value of L could tureofequations(24)–(28),whichfacilitatesusingveryhigh-
in principle be imprinted in subtle finite size effects that performancefastFouriertransforms.
c (x,[ρ]) has acquired, the size L of the original simulation Weshowthreerepresentativeexamplesofdensityprofiles
1
boxhasvanishedandtheapplicationoftheneuralfunctional fornarrowtowideconfinementbetweenimpenetrablewallsin
inequation(29)isfitforusetopredictpropertiesofmuchlar- figure6.Inallcasestheresultsfromusingtheneuralfunctional
gersystems.Asanexample,[41]demonstratesthescalingup arenumericallyidenticaltothosefromthePercusfunctional
byafactorof100fromtheoriginalsimulationboxtothepre- onthescaleoftheplot.Theprofilesinnarrow(figure6(a))and
dictedsystemofthree-dimensionalhardspheresundergravity. inmoderatelywide(figure6(b))poresshowverydinstinctfea-
Thenumericalsolutionofequation(29)canbeefficiently tureswiththestronglyconfinedsystemin(a)havingastrik-
performed on the basis of Picard iteration where an initial ingV-shape,whicharisesfromhavingatmosttwoparticlesin
guessof thedensity profile isinserted on theright hand side thesystem,tothemoregenericdampedoscillatorybehaviour
and the resulting left hand side is used to nudge the initial in the moderately wide pore (b). The main panel figure 6(c)
11

| J.Phys.:Condens.Matter36(2024)243002 |     |     |     |     |     |     |     |     |     |     |     |     |     | TopicalReview |
| ------------------------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ------------- |
shows the influence of a weak gravitational field, which cre- the particles, via the neural functional c (x,[ρ]), begs for
1
atesacontinuouslyvaryingdensityinhomogeneityacrossthe speculation whether additional and as yet hidden physical
entiresystem.Thedecayinlocaldensityoccurswithamuch structurecanberevealed.Wegivetwoplausibilityarguments
(x,[ρ])ina
largerlengthscaleascomparedtotheparticlepackingeffects whyoneshouldexpecttobeabletopostprocessc
1
thatarelocalizednearthelowerwall. meaningfulwaytoretrieveglobalinformation.
The behaviour shown in figure 6(c) away from the walls First, thermodynamics is based on the existence of very
iswell-representedbyalocaldensityapproximation[8](see fewandwell-defineduniqueandglobalquantities,suchasthe
e.g. [113] for recent mathematical work). The local dens- entropy,theinternalenergy,andthefreeenergy.Carryingout
ity approximation can be a useful tool when investigating parametric derivatives, with powerful interrelations given by
e.g.macroscopicorderingundergravity,wheretheoccurring theMaxwellrelations,enablesonetoobtainequationsofstate,
stackingsequencesofdifferentthermodynamicphasescanbe susceptibilitiesandfurthermeasurableglobalquantities.Our
tracedbacktothephasediagram[114,115].Inparticularthe neuraldirectcorrelationfunctionalincontrastisalocalobject
effectsonmixtureswererationalizedbyarangeoftechniques, withfiniterangeofnonlocality.Sohowdoesthisrelatetothe
from generalization of Archimedes’ principle [116, 117] to globalinformation?
analyzing stacking sequences [114, 115]. We stress that the Thesecondargumentismoreformal.Supposeweprescribe
present model applications constitute very significant extra- the form of the density profile and then evaluate the neural
polations from the training data that we recall was obtained functionalc (x,[ρ])ateachpositionx.Thisprocedureyieldsa
1
in a fixed box size L=10σ and under the influence of ran- numericalrepresentationofthecorrespondingdirectcorrela-
(x).Inthepracticalnumericalimplementation
| domizedexternalandchemicalpotentials.Thisisrelevantin |     |     |     |     |     |     | tionfunctionc |     | 1   |     |     |     |     |     |
| ----------------------------------------------------- | --- | --- | --- | --- | --- | --- | ------------- | --- | --- | --- | --- | --- | --- | --- |
particularforboththeveryconfinedsystem(figure6(b))and we have a set of discrete grid points that represent the func-
thelargesystem(figure6(c)). tion values at these spatial locations x. Hence the entire data
As a further potential application of the neural functional setformsanumericalarrayornumericalvector,indexedbyx.
theory, the dynamical density functional theory [5, 69, 118] Onecanthenaskwhetherthisvectorcouldpotentiallybethe
is similarly easy to implement numerically as equation (29) gradientofanoverarchingparentobject?
and it is a currently popular choice to study time-dependent Thephysicalandtheformalquestioncanbothbeanswered
problems [119, 120]. We comment on the status of the affirmatively due to the existence of the excess free energy
approach[40]andhowmachinelearningcanhelptoovercome densityfunctionalF [ρ].Itspracticalrouteofaccess,based
exc
itslimitationsinsection4below. on functional integration along a continuous sequence of
|     |     |     |     |     |     |     | states | (a ‘line’)      | in  | the space | of density |         | functions, | is strik-   |
| --- | --- | --- | --- | --- | --- | --- | ------ | --------------- | --- | --------- | ---------- | ------- | ---------- | ----------- |
|     |     |     |     |     |     |     | ingly  | straightforward |     | within    | the neural | method. |            | The core of |
3. Neuralfunctionalcalculus the method is to evaluate c (x,[ρ ]) as described above, but
|     |     |     |     |     |     |     |     |     |     |     | 1 a |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
forarangeofscaledversionsoftheprescribeddensityprofile
Wehaveseeninsection2howaneuralone-bodydirectcorrel- ρ (x)andthenintegratinginpositiontoobtaintheexcessfree
a
ationfunctionalcanbeefficientlytrainedonthebasisofapool
|                                                        |     |     |     |     |     |     | energy       | as a | global | value, | see the functional |     | integral | given in |
| ------------------------------------------------------ | --- | --- | --- | --- | --- | --- | ------------ | ---- | ------ | ------ | ------------------ | --- | -------- | -------- |
| ofpre-generatedMonteCarlosimulationdatathatareobtained |     |     |     |     |     |     | equation(9). |      |        |        |                    |     |          |          |
underrandomizedconditions.Thespecificwayoforganizing Specifically,wedefineascaledversionofthedensitypro-
| the simulation | data | into training | sets | mirrors | the | functional |         |              |     |      |          |           |     |           |
| -------------- | ---- | ------------- | ---- | ------- | --- | ---------- | ------- | ------------ | --- | ---- | -------- | --------- | --- | --------- |
|                |      |               |      |         |     |            | file as | ρ (x)=aρ(x), |     | such | that a=0 | generates |     | the empty |
a
relationshipsgivenbyclassicaldensityfunctionaltheory.We state that has vanishing density profile, ρ (x)=0. On the
a=0
| have then | shown | that the neural | functional |     | can efficiently | be  |       | a=1 |        |     |                |     |         |              |
| --------- | ----- | --------------- | ---------- | --- | --------------- | --- | ----- | --- | ------ | --- | -------------- | --- | ------- | ------------ |
|           |       |                 |            |     |                 |     | other | end | yields | the | actual density |     | profile | of interest, |
usedtoaddressphysicalproblems,takingtheone-dimensional ρ (c)=ρ(x). The excess free energy functional is then
a=1
hardrodsystemasasimpleexampleofamutuallyinteracting obtainedeasilyviafunctionalintegrationaccordingto
many-bodysystem.
|     |     |     |     |     |     |     |     |     |     | ˆ   | ˆ   |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
1
| We here                                              | proceed | by exemplifying |     | the | depth of | physical |     |     |       |     |        |     |       |          |
| ---------------------------------------------------- | ------- | --------------- | --- | --- | -------- | -------- | --- | --- | ----- | --- | ------ | --- | ----- | -------- |
|                                                      |         |                 |     |     |          |          |     | βF  | [ρ]=− |     | dxρ(x) | dac | (x,[ρ | ]). (30) |
| insightthatcanbeexploredbyacknowledgingthefunctional |         |                 |     |     |          |          |     |     | exc   |     |        | 1   | a     |          |
0
| character | of the | trained neural | correlation |     | functional. | Hence |     |     |     |     |     |     |     |     |
| --------- | ------ | -------------- | ----------- | --- | ----------- | ----- | --- | --- | --- | --- | --- | --- | --- | --- |
welayoutfunctionalintegration(section3.1)andfunctional Thenumericalevaluationrequiresevaluatingc (x,[ρ a ])atall
1
differentiation (section 3.2). We show sum rule construction positionsxinthesystemandforarangeofintermediateval-
|     |     |     |     |     |     |     |     | ⩽ ⩽ |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
viaNoetherinvariance(section3.3),viaexchangesymmetry ues0 a 1suchthattheparametricintegraloveracanbe
(alsosection3.3),andviafunctionalintegration(section3.4). accuratelydiscretized.
Analyticallycarryingoutthefunctionalintegral(30)onthe
Thepresentationineachsubsectionisself-containedtoacon-
siderabledegreeandweillustratethegeneralityofthemeth- basis of the analytical direct correlation functional c 1 (x,[ρ])
odsbothbyapplicationtotheneuralfunctionalaswellasby as given by equations (24)–(28) is feasible. The result [56],
revisitingtheanalyticPercustheory. again expressed in the more illustrative Rosenfeld funda-
mentalmeasureform,isgivenby:
ˆ
3.1. Functionalintegrationofdirectcorrelations
|     |     |     |     |     |     |     |     |     | βF  | [ρ]= | dxΦ(n | (x),n | (x)), | (31) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---- | ----- | ----- | ----- | ---- |
|     |     |     |     |     |     |     |     |     |     | exc  |       | 0     | 1     |      |
Havingcapturedtheessenceofmolecularpackingeffects,as
|                                                      |     |     |     |     |     |     |     | Φ(n | (x),n | (x))=− | n (x)ln[1 | −   | n (x)]. | (32) |
| ---------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | ----- | ------ | --------- | --- | ------- | ---- |
| theyarisefromtheshort-rangedhardcorerepulsionbetween |     |     |     |     |     |     |     |     | 1     | 2      | 0         |     | 1       |      |
12

| J.Phys.:Condens.Matter36(2024)243002 |     |     |     |     |     |     |     |     |     |     |     |     |     | TopicalReview |
| ------------------------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ------------- |
Here the integrand Φ(n (x),n (x)) plays the role of a local- In more compact notation we can express equation (37) as
|     |     |     | 0   | 1   |     |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
∗ρ)(x),
izedexcessfreeenergydensitywhichdependsontheweighted nα (x)=(wα where the asterisk denotes the spatial
densities n (x) and n (x) as given via the spatial averaging convolution.Thenthedirectcorrelationfunctionalisgivenby
|                                                         | 0   | 1   |     |     |     |     |     |     |     |     |     |     |     |     |
| ------------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| proceduresinequations(27)and(28),respectively.Inserting |     |     |     |     |     |     |     |     |     |     | X   |     |     |     |
equation(32)intoequation(31)yieldsthehardrodexcessfree c (x,[ρ])=− (wα ∗Φ )(x), (38)
|     |     |     |     |     |     |     |     |     | 1   |     |     |     | α   |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
energyfunctionalinthefollowingmoreexplicitform:
α=0,1
ˆ
whichisanexactrewritingoftheformgiveninequation(24).
|     | βF  | [ρ]=− | dxn | (x)ln[1 | − n (x)]. | (33) |     |     |     |     |     |     |     |     |
| --- | --- | ----- | --- | ------- | --------- | ---- | --- | --- | --- | --- | --- | --- | --- | --- |
exc 0 1 The functions Φ are obtained as partial derivatives of the
α
|     |     |     |     |     |     |     | scaledfreeenergydensity(32)viaΦ |     |     |     |     | =∂Φ/∂nα.Thisderiv- |     |     |
| --- | --- | --- | --- | --- | --- | --- | ------------------------------- | --- | --- | --- | --- | ------------------ | --- | --- |
α
Equation(33)isstrikinglycompact,giventhatitdescribesthe ative structure reveals the mechanism for the generation of
essenceofasystemofmutuallyinteractinghardcoresexposed the explicit forms Φ (x) and Φ (x), as respectively given by
|                                 |     |     |     |     |     |     |                       |     |     | 0   | 1   |     |     |     |
| ------------------------------- | --- | --- | --- | --- | --- | --- | --------------------- | --- | --- | --- | --- | --- | --- | --- |
| toanarbitraryexternalpotential. |     |     |     |     |     |     | equations(25)and(26). |     |     |     |     |     |     |     |
Althoughtheresultofthefunctionalintegral(30)haslost
allpositiondependence,thespecificformofthedensitypro-
3.2. Functionaldifferentiationofdirectcorrelations
| file ρ(x) | is deeply | baked | into | the | resulting output | value of |     |     |     |     |     |     |     |     |
| --------- | --------- | ----- | ---- | --- | ---------------- | -------- | --- | --- | --- | --- | --- | --- | --- | --- |
the functional via both the prefactor ρ(x) in the integrand in Whiletheabovedescribeduseoffunctionaldifferentiationin
equation(30)andtheevaluationofthedirectcorrelationfunc- ananalyticalsettingmightappeartobeveryformalandper-
tionalatthespecificallyscaledformρ (x).Inparallelwiththis hapslimitedinitsapplicability,weemphasizethattheconcept
a
mathematical structure, the explicit form (33) of the Percus isindeedverygeneral.Givenaprescribedfunctionalofafunc-
functional clearly demonstrates that the resulting value will tion ρ(x), the functional derivative δ/δρ(x) simply gives the
dependnontriviallyontheshapeoftheinputdensityprofile. gradientofthefunctionalwithrespecttoachangeintheinput
Having demonstrated that F [ρ] as a global quantity can functionataspecificlocationx.
exc
be obtained from appropriate functional integration of a loc- By applying the functional derivative in the present one-
|     |     |     |     |     | (x,[ρ]) |     |     |     |     |     |     |     |     | (x,[ρ]), |
| --- | --- | --- | --- | --- | ------- | --- | --- | --- | --- | --- | --- | --- | --- | -------- |
ally resolved correlation functional c 1 naturally leads dimensional context to a given functional form of c 1
tothe questionwhether areversepathexiststhatwouldmir- oneobtainsthetwo-bodydirectcorrelationfunctionalandwe
rortheinversestructureprovidedbyintegrationanddifferen- recallthegenericexpression(12):
tiationknownfromordinarycalculus.
Theavailabilityofacorrespondingderivativestructurefor ′ δc (x,[ρ])
|     |     |     |     |     |     |     |     |     | c   | (x,x ,[ρ])= |     | 1       | .   | (39) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ----------- | --- | ------- | --- | ---- |
|     |     |     |     |     |     |     |     |     | 2   |             |     | δρ(x ′) |     |      |
functionalsisquitesignificant,asthisbyconstructiongener-
atesspatialdependence,asindicatedbyδ/δρ(x);seee.g.[9]
fordetails.Wecanhenceretrieve,orgenerate,thedirectcor- Using the Percus version (38) of the one-body direct cor-
|          |            |        |            |     |                    |        | relation | functional | and | carrying | out | the functional |     | derivative |
| -------- | ---------- | ------ | ---------- | --- | ------------------ | ------ | -------- | ---------- | --- | -------- | --- | -------------- | --- | ---------- |
| relation | functional | as the | functional |     | density derivative | of the |          |            |     |          |     |                |     |            |
intrinsicexcessfreeenergyfunctional: ontherighthandsideofequation(39)givesviaananalytical
calculationthefollowingnonlocalresult:
X
|     |     |             |     | δβF | [ρ]     |      |     |        |           |     |         |          |     |         |
| --- | --- | ----------- | --- | --- | ------- | ---- | --- | ------ | --------- | --- | ------- | -------- | --- | ------- |
|     |     | c (x,[ρ])=− |     |     | e x c . | (34) |     |        | ′ ,[ρ])=− |     | ∗Φ      | ∗        | ′   |         |
|     |     | 1           |     | δρ  | ( )     |      |     | c (x,x |           |     | (wα αα′ | wα′)(x,x |     | ). (40) |
|     |     |             |     |     | x       |      |     | 2      |           |     |         |          |     |         |
αα′
| While | we  | turn to more | general |     | functional differentiation |     |     |      |            |          |             |     |           |      |
| ----- | --- | ------------ | ------- | --- | -------------------------- | --- | --- | ---- | ---------- | -------- | ----------- | --- | --------- | ---- |
|       |     |              |         |     |                            |     | We  | make | the double | asterisk | convolution |     | structure | more |
below,wehereaddressagaintheanalyticalcase,whichisuse-
|     |     |     |     |     |     |     | explicit | below. | The | coefficient | functions |     | in equation | (40) |
| --- | --- | --- | --- | --- | --- | --- | -------- | ------ | --- | ----------- | --------- | --- | ----------- | ---- |
fulasitrevealstheoriginofthedoubleappearanceofthetwo
|     |     |     |     |     |     |     | are | obtained | as second |     | partial | derivatives | via | Φ αα′ = |
| --- | --- | --- | --- | --- | --- | --- | --- | -------- | --------- | --- | ------- | ----------- | --- | ------- |
spatialweightingprocessesinequations(24)–(28).Rosenfeld
|                                   |     |     |     |     |         |           | ∂2Φ/∂nα | ∂nα′.    | Explicitly, |                                 | we have | Φ (x)=0 | and | the sym- |
| --------------------------------- | --- | --- | --- | --- | ------- | --------- | ------- | -------- | ----------- | ------------------------------- | ------- | ------- | --- | -------- |
|                                   |     |     |     |     | (x)andw | (x),which |         |          |             |                                 |         | 00      |     |          |
| [61]introducedtwoweightfunctionsw |     |     |     |     | 0       | 1         |         |          |             |                                 |         |         |     |          |
|                                   |     |     |     |     |         |           | metryΦ  | 01 (x)=Φ | 10          | (x).Theremainingtermsaregivenby |         |         |     |          |
respectivelydescribetheendpointsofaparticleanditsinterior
one-dimensional‘volume’:
1
|     |     |           |       |           |     |      |     |     | Φ   | (x)= |      | ,     |     | (41) |
| --- | --- | --------- | ----- | --------- | --- | ---- | --- | --- | --- | ---- | ---- | ----- | --- | ---- |
|     |     |           |       |           |     |      |     |     |     | 01   | −    | (x)   |     |      |
|     |     |           | δ(x − | R)+δ(x+R) |     |      |     |     |     |      | 1 n  | 1     |     |      |
|     |     | w (x)=    |       |           | ,   | (35) |     |     |     |      |      | (x)   |     |      |
|     |     | 0         |       | 2         |     |      |     |     |     |      | n 0  |       |     |      |
|     |     |           |       |           |     |      |     |     | Φ   | (x)= |      |       | .   | (42) |
|     |     |           |       | −| |),    |     |      |     |     |     | 11   | [1 − | (x)]2 |     |      |
|     |     | w (x)=Θ(R |       | x         |     | (36) |     |     |     |      | n    | 1     |     |      |
1
Θ(x) Inserting these results into equation (40) and making the
| where |     | indicates | the Heaviside |     | unit step | function, i.e. |     |     |     |     |     |     |     |     |
| ----- | --- | --------- | ------------- | --- | --------- | -------------- | --- | --- | --- | --- | --- | --- | --- | --- |
convolutionsexplicityieldsthefollowingexpression:
| Θ(x ⩾ | 0)=1 | and 0 otherwise. |     | The | weighted densities | n (x) |     |     |     |     |     |     |     |     |
| ----- | ---- | ---------------- | --- | --- | ------------------ | ----- | --- | --- | --- | --- | --- | --- | --- | --- |
0
|     | ( ) |     |     |     |     |     |     |     |     | ˆ   |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
a n d n 1 c , a s g i v e n re sp ec t iv e l y b y e qu a ti o n s ( 2 7 ) a n d (2 8) , c a n (x − ′′)w (x ′− ′′)
|     |     |     |     |     |     |     |     | ′ ,[ρ])=− |     | ′′w | 0   | x   | 1 x |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --------- | --- | --- | --- | --- | --- | --- |
t h e n b e r e p r e s e n t ed v ia c o n v o lu t io n o f t h e r e s p e c ti ve w e i g h t c (x,x 2 dx
|                                                     |     |         |       |      |           |      | 2   |     |     |     | 1    | − n (x | ′′)      |        |
| --------------------------------------------------- | --- | ------- | ----- | ---- | --------- | ---- | --- | --- | --- | --- | ---- | ------ | -------- | ------ |
| functionoftypeα=0,1withthedensityprofileaccordingto |     |         |       |      |           |      |     |     | ˆ   |     |      | 1      |          |        |
|                                                     |     |         |       |      |           |      |     |     |     |     | −    | ′′)n   | ′′)w     | ′− ′′) |
|                                                     |     |         |       |      |           |      |     |     |     | ′′w | (x x | (x     | (x       | x      |
|                                                     |     |         | ˆ     |      |           |      |     |     | −   | dx  | 1    | 0      | 1        | .      |
|                                                     |     |         | ′     |      | ′ ′       |      |     |     |     |     |      | [1 − n | (x ′′)]2 |        |
|                                                     |     | nα (x)= | dx wα | (x − | x )ρ(x ). | (37) |     |     |     |     |      |        | 1        |        |
(43)
13

| J.Phys.:Condens.Matter36(2024)243002 |     |     |     |     |     | TopicalReview |     |
| ------------------------------------ | --- | --- | --- | --- | --- | ------------- | --- |
We recall the definitions (35) and (36) of the weight func- the microscopic spatial liquid structure beyond the pair cor-
tionsw (x)andw (x).Theconvolutionstructurecouplestwo relation function for a broad range of model fluids [96, 98].
| 0   | 1   |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- |
weight functions together and each of them has a range of Noetherinvarianceisrelevantforanythermalobservable,as
R.Henceindeedthetwo-bodydirectcorrelationsareoffinite associatedsumrulescouplethegivenobservabletoforcesvia
|     |     | − ′ |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- |
range2R=σinthepositiondifferencex x [55]. veryrecentlyidentifiedhyperforcecorrelations[97].
While the above results for the Percus theory have been The statistical Noether sum rules are exact identities that
derived by pen-and-paper symbolic calculations, the neural canserveavarietyofdifferentpurposes,rangingfromtheory
functional is not amenable to such conventional techniques. buildingviacombinationwithapproximateclosurerelations,
Fortunately, the framework of automatic differentiation [99] testingforsufficientsamplinginsimulation[97],carryingout
provides a powerfulalternativeto both symbolic and numer- forcesamplingtoimprovestatisticaldataqualityand,lastbut
ical differentiation methods, and it is a natural choice to notleast,testingneuralfunctionals[40,41].Havingthelatter
consider in the context of machine learning [100]. Via the purposeinmind,herewedescribeaselectionoftheseNoether
implementationofeithermodifiedalgebraorofcomputational identities.
graphs, automatic differentiation facilitates to obtain derivat- As a fundamental property, the interparticle interaction
ivesdirectlyintheformofexecutablecode,andcruciallythere potential only depends on the relative particle positions and
is no need of any manual intervention. Automatic differenti- not on the absolute particle coordinate values. Specifically,
ationtherebyisfreeofthenumericalartifactsthataretypical whethertwoparticlesoverlapintheone-dimensionalsystem
offinitedifferenceschemes.Themethodisapplicableinbroad is unaffected by displacing the entire microstate uniformly.
contexts,whichweillustrateintheonlinetutorial[42]bycom- This invariance against global translation leads to associated
′,[ρ])viaautomaticdifferen-
putingthePercusresultforc (x,x sum rules for direct correlation functions; we recall that the
2
tiationofequation(38)ratherthanbymanualimplementation direct correlations arise solely from the interparticle interac-
ofequation(43). tionsandhencetheyarenotdirectlydependentontheexternal
Forcompleteness,wecanrecovertheone-bodydirectcor- potential. We quote two members of an infinite hierarchy of
relation functional by functional integration. We reproduce identities, which is originally due to Lovett, Mou, Buff, and
equation(11)forthepresentone-dimensionalgeometry: Wertheim[129, 130],seeequations(45)and(46)below.We
groupthesetogetherwitharecentcurvaturesumrule(47)[92].
|     | ˆ   | ˆ   |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- |
1 Ultimatelytheidentities(45)and(46)expressthevanishingof
|     | ′   | ′ ′ |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- |
c (x,[ρ])= dx ρ(x ) dac (x,x ,[ρ ]). (44) theglobalinterparticleforce,asobtainedbysummingoverthe
| 1   |     | 2   | a   |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- |
0
|     |     |     | interparticle | forces on | all particles. | The three sum rules | read |
| --- | --- | --- | ------------- | --------- | -------------- | ------------------- | ---- |
asfollows:
Onthebasisoftheneuralrepresentationsofthedirectcorrela-
ˆ
tionfunctionals,thisidentitycanbeusedtocheckforconsist-
|                                                     |     |     |     | dxρ(x)∇ | c (x,[ρ])=0, |     | (45) |
| --------------------------------------------------- | --- | --- | --- | ------- | ------------ | --- | ---- |
| encyandforcorrectnessoftheautomaticdifferentiation. |     |     |     |         | 1            |     |      |
ˆ ˆ
|     |     |     |     | dxρ(x) | ′ ρ(x ′ )∇ | (x,x ′ ,[ρ])=0, |      |
| --- | --- | --- | --- | ------ | ---------- | --------------- | ---- |
|     |     |     |     |        | dx c 2     |                 | (46) |
3.3. Noetherinvarianceandexchangesymmetry
|     |     |     |     | ˆ         | ˆ     |     |     |
| --- | --- | --- | --- | --------- | ----- | --- | --- |
|     |     |     |     | dx[∇ρ(x)] | ′ [∇′ | ′ ′ |     |
In its standard applications Noether’s theorem is used to dx ρ(x )]c (x,x ,[ρ])
2
| relatesymmetriesofadynamicalphysicalsystemwithasso- |     |     |     | ˆ   |     |     |     |
| --------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
ciatedconservationlaws.Obtaininglinearmomentumconser- =− dxρ(x)∇∇ c (x), (47)
1
vationfromasymmetryoftheunderlyingactionintegralisa
| primary example, | see e.g. [91] | for an introductory | presenta- |     |     |     |     |
| ---------------- | ------------- | ------------------- | --------- | --- | --- | --- | --- |
tion.Besidessuchdeterministicapplications,theNoetherthe- whereintheone-dimensionalsystemthegradientisasimple
oremiscurrentlyseeinganincreaseduseinavarietyofstat- scalarpositionderivative, ∇=d/dx.Briefly,equation(45)is
|     |     |     |     |     | [ρ]=F | [ρ ],wherethedisplaced |     |
| --- | --- | --- | --- | --- | ----- | ---------------------- | --- |
isticalmechanicalsettings[121–128]. obtainedbynotingthatF exc exc ϵ
TherecentstatisticalNoetherinvariancetheory[90–98]is densityprofileisgivenbyρ (r)=ρ(r+ϵ)withdisplacement
ϵ
based on specific spatial displacement (‘shifting’) and rota- vectorϵ(inthreedimensionalsystems).Buildingthegradient
]/∂ϵ|
tionoperations.Thesetransformationsarecarriedoutinthree- w´ith respect to ϵ yields the result 0=∂βF [ρ ϵ ϵ=0 =
exc
dimensional physical space and their effect is traced back to dr(δβF [ρ]/δρ(r))∇ρ(r),whichgivesequation(45)upon
exc
underlying invariances on the high-dimensional phase space integration by parts, resorting to the one-dimensional geo-
anditsassociatedthermalandnonequilibriumensembles. metry, and identifying the one-body direct correlation func-
ThecentralstatisticalNoetherinvarianceconcept[90,91] tionalviaequation(34);formoredetailsofthederivationwe
wasdemonstratedinarangeofstudies,addressingthestrength refer the Reader to [90, 91]. Equation (46) is then obtained
of force fluctuations via their variance [92], the formula- as the density functional derivative of equation (45) and re-
tion of force-based classical density functional theory [93, using equation (45) to simplify the result. Equation (47) is a
94], and the force balance in quantum many-body systems curvature sum rule that follows from spatial Noether invari-
[95]. The invariance theory has led to the discovery of anceatsecondorderintheglobalshiftingparameterϵ[90].
force-forceandforce-gradienttwo-bodycorrelationfunctions. Usingalocallyresolvedshiftingoperation,wherethedis-
Thesecorrelatorswereshowntodeliverprofoundinsightinto placementϵ(r)islocalanddependsonthespatialpositionr
14

J.Phys.:Condens.Matter36(2024)243002 TopicalReview
and hence constitutes a vector field (in the case of a three-
dimensional system), yields in one dimension the following
position-resolvedidentity:
ˆ
∇ c (x,[ρ])= dx ′ c (x,x ′ ,[ρ])∇′ ρ(x ′ ). (48)
1 2
The left hand side has the direct interpretation of the mean
interparticle force field, expressed in units of the thermal
energy k T. This force both acts in equilibrium and it drives
B
theadiabaticpartofthetimeevolutioninnonequilibrium[9];
wedescribesomedetailsofthenonequilibriumtheoryfortime
evolutioninsection4.
When inserting the relationship (34) of c (x,[ρ]) to the
1
free energy functional F [ρ] into the definition (39) of
exc
c (x,x ′,[ρ])weobtain
2
c (x,x ′ ,[ρ])=−
δ2βF
exc
[ρ]
, (49)
2 δρ(x)δρ(x ′)
whichistheone-dimensionalversionofthegeneralrelation-
ship(14).Astheorderofthetwofunctionalderivativesisirrel-
evantweobtainthefollowingexactsymmetrywithrespectto
theexchangeofthetwopositionarguments:
′ ′
c (x,x ,[ρ])=c (x ,x,[ρ]). (50)
2 2
Whenappliedtotheneuralfunctional,theexchangesymmetry
relationship(50)ishighlynontrivial,asthedensitywindows
thatenterthefunctionalsontheleftandontherighthandsides
differmarkedlyfromeachother,asdothecorrespondingeval-
uation positions. That both displacement effects cancel each
otherandleadtotheidentity(50)isnontrivialandcanserve
bothfortestingthequalityoftheneuraldirectcorrelationfunc-
tional and for demonstrating the existence of an overarching
grandmotherfunctionalF [ρ].
exc
In order to illustrate the theoretical structure, we display
numericalresultsinfigure7.Weselectarepresentativeoscil-
Figure7. NumericalresultsforfunctionalcalculusandNoether
latorydensityprofile,asshowninfigure7(a),andtakethisas
invariance.Theresultsareshownforanexemplaryoscillatory
aninputtoevaluatetheone-bodydirectcorrelationfunctional densityprofiledisplayedinpanel(a).Resultsfortheneural
c 1 (x,[ρ]). This procedure yields a specific form of the dir- predictionforc 1 (x)arecomparedtonumericallyevaluatingPercus’
ectcorrelationfunctionc (x),displayedinfigure7(b),which analyticaldirectcorrelationfunctional(24)inpanel(b).The
belongstotheprescribedd 1 ensityprofileρ(x).Thespatialvari- two-bodydirectcorrelationfunctionc 2 (x,x ′)asafunctionofx/σ
andx
′/σ,asobtainedfromautomaticdifferentiationoftheneural
ations of ρ(x) and c (x) are roughly out-of-phase with each
1 functionalisshowninpanel(c)andcomparedtotheresultfrom
other. The nonlinear and nonlocal nature of the functional usingPercus’analyticalexpression(43)inpanel(d).Usingthe
relationshipρ→
c 1 ishoweververyapparentintheplot.The neuralfunctionals,theagreementoftheleftandrighthandsideof
results from choosing the neural functional or Percus’ ana- theNoetherforcesumrule(48)isshowninpanel(e).Inallcases
theneuralfunctionalandPercustheoriesgivenumericallyidentical
lyticalone-bodydirectcorrelationfunctionalagreewitheach
resultsonthescaleoftherespectiveplot.
othertoexcellentaccuracy.Theagreementisdemonstratedin
figure7(b),wherethetworesultingdirectcorrelationprofiles
areidenticalonthescaleoftheplot.
Aslaidoutabove,theexchangesymmetry(50)constitutes AsarepresentativecasefortheuseofaNoethersumrule
a rigorous test for the two-body direct correlation functional asaquantitativetestfortheaccuracyoftheneuralfunctional
c (x,x ′,[ρ]).Boththeneuralandtheanalyticalfunctionalpass methods,weshowinfigure7(e)thenumericalresultsofeval-
2
withflyingcolours,seefigures7(c)and(d)respectively,where uatingbothsidesofequation(48)forthesamegivendensity
the symmetry of the respective ‘heatmap’ graph against mir- profile (shown in figure 7(a)). We find that both sides of the
roringatthediagonalisstrikinglyvisible. equationagreewithhighnumericalprecisionwitheachother.
15

J.Phys.:Condens.Matter36(2024)243002 TopicalReview
3.4. Functionalintegralsumrules relationship between the two- and three-body direct correla-
tionfunctionals:
We next address general identities that emerge from exploit-
ˆ
ingthe inversenature of functionaldifferentiationand integ- 1
′ ′
ration. For this, we recall the functional integral form (9) of c 2 (r,r ,[ρ])= dac 2 (r,r ,[ρ a ])
F [ρ] and the functional derivative form (10) of c (r,[ρ]), 0ˆ ˆ
exc 1 1
which both are central for the following derivations. That + dr ′′ ρ(r ′′ ) daac (r,r ′ ,r ′′ ,[ρ ]).
3 a
equation(9)istheinverseofequation(10)canbeseenexpli- 0
citlybyfunctionallydifferentiatingequation(9)asfollows: (53)
ˆ ˆ
δβ δ F ρ e ( x r c ) [ρ] =− dr ′ 1 da δρ δ (r) ρ(r ′ )c 1 (r ′ ,[ρ a ]). (51) T c 3 h ( e r,r ′ n , e r u ′′ r , a [ l ρ]) f v u i n a ct a i u o t n o a m l ati c c al g c e u n l e u r s atio a n llo o w f s the t H o ess o ia b n ta o in f
0 c (r,[ρ]) [41], which elevates equation (53) beyond mere
1
Wehaveinterchangedtheorderofintegrationandfunctional formalinterest.
differentiationontherighthandsideofequation(51)asthese Thestructureofequations(52)and(53)expressesageneral
operationsareindependentofeachother.Thefunctionaldens- functionalrelationship.Whenappliedtotheexcessfreeenergy
ity derivative now acts on the product ρ(r ′)c (r ′,[ρ ]) and functionalitselftheresultis:
1 a
ˆ
weneedtodifferentiatebothfactorsaccordingtotheproduct
1
rule. Differentiating the first factor gives the Dirac distri- βF [ρ]= daβF [ρ ]
exc exc a
bution, δρ(r ′)/δρ(r)=δ(r − r ′). Differentiating the second 0ˆ ˆ
factor generates the two-body direct correlation functional 1
according to equation (39) and hence δc (r ′,[ρ ])/δρ(r)= − drρ(r) daac 1 (r,[ρ a ]). (54)
ac (r,r ′,[ρ ]), where multiplication by th 1 e scali a ng factor a 0
2 a
arisesfromtheidentityδ/δρ(r)=aδ/δ(aρ(r))=aδ/δρ (r). We furthermore demonstrate explicitly the relationship
a
We can hence reformulate equation (51) by rewriting the from daughter to grandmother via functional integration of
lefthandsideviaequation(10)andexpressingtherighthand the two-body correlation functional to obtain the excess free
sidebythetwoseparateterms.Uponmultiplicationby − 1the energyfunctional:
resultisthefollowingfunctionalintegralidentity: ˆ ˆ
ˆ βF [ρ]=− drρ(r) dr ′ ρ(r ′ )
1 exc
c (r,[ρ])= dac (r,[ρ ]) ˆ ˆ
1 1 a 1 a
0ˆ ˆ
1
× da da ′ c
2
(r,r ′ ,[ρ a′]), (55)
′ ′ ′ 0 0
+ dr ρ(r ) daac (r,r ,[ρ ]). (52)
2 a
0 whereagainthescaleddensityprofileisρ a′(r)=a ′ρ(r).That
In the first term on the right hand side of equation (52) the equation(55)holdscanbeseenbychainingtogetherthetwo
positionintegralhascancelledoutduetothepresenceofthe levels of functional integrals (9) and (44) and then simplify-
Diracfunction,whichleavesoverthepositiondependenceon ing the two nested parameter integrals. The double paramet-
r,asoccurringinallotherterms. ricintegralinequation(55)can´alternat´ivelybewrittenwith
In order to prove equation (52) and hence to estab- fixed parametric boundaries as 0 1 daa 0 1 da ′ c 2 (r,r ′,[ρ aa′]),
lish that indeed equations (9) and (10) are inverse of each wherethetwicescaleddensityprofileisdefinedasρ aa′(r)=
other, we integrate by parts in a addressing the first integ- aa
′ρ(r).
ral on the right hand side of equation (52). This yields E´vans[´7]goesfurther´thanequation(55)byusingtheiden-
´a sum of boundary terms and an integral: c
1
(r,[ρ])− 0 − tity
0
1 da
0
a da ′ f(a ′)=
0
1 da(1 − a)f(a), which is valid for
1 daa∂c (r,[ρ ])/∂a.Thederivativewithrespecttothepara- any function f(a), as can either by shown geometrically by
0 1 a
meter a generatesthe second term in equation (52)up to the consideringthetriangle-shapedintegrationdomaininthetwo-
minus si´gn upon carrying out the parametric derivative via dimensional(a,a ′)-planeor,moreformally,byintegrationby
∂/∂a= dr ′ρ(r ′)δ/δρ (r ′) and identifying c (r,r ′,[ρ ])= parts. The identity allows to express equation (55) in a form
a 2 a
δc (r,[ρ ])/δρ (r ′). Hence the two integrals cancel each thatrequirestocarryoutonlyasingleparametricintegral:
1 a a
other.Onlytheupperboundarytermc (r,[ρ])remains,which ˆ ˆ
1
isthelefthandsideofequation(52),andhencecompletesthe βF [ρ]=− drρ(r) dr ′ ρ(r ′ )
exc
proof. ˆ
Despite this explicit derivation via functional calculus, as 1
bothc (r,[ρ])andc (r,r ′,[ρ])aredirectlyavailableasneural × da(1 − a)c 2 (r,r ′ ,[ρ a ]). (56)
1 2 0
functionals,thefunctionalintegralsumrule(52)providesyet
againfreshpossibilityforcarryingourconsistencyandaccur- Evans [7] also considers more general cases where the para-
acychecks. meteralinearlyinterpolatesbetweenanontrivialinitialdens-
Goingthroughtheanalogouschainofargumentsonegen- ity profile ρ(r)̸=0 and the target profile ρ(r) via ρ (r)=
i a
eration younger leads to the following functional integral
ρ(r)+a[ρ(r)−ρ(r)].
In our present description we have
i i
16

| J.Phys.:Condens.Matter36(2024)243002 |     |     |     |     |     |     |     |     |     |     |     |     |     | TopicalReview |
| ------------------------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ------------- |
restricted ourselves to empty initial states, ρ(r)=0, but the wasshowntocapturecorrectlytheessenceoftheforcesthat
i
functionalintegrationmethodologyismoregeneral,see[7]. occurinthenonequilibriumsituation.Togetherwiththeexact
Throughoutwehavenotatedthefunctionalintegralsviaan force balance equation, this allows to predict and to design
outerpositionintegraloverrandaninnerparametricintegral nonequilibriumsteadystates[40].Theapproachoffersasys-
over a.This structure allowsto takethecommon factorρ(r) tematicwaytogobeyonddynamicaldensityfunctionaltheory
outoftheinnerintegral.Standardpresentationsoftenreverse andtoaddressgenuinenonequilibriumbeyondafreeenergy
theorderofintegration.Takingthefunctionalintegraloverthe description. We recall studies based on dynamical density
one-bodydirectcorrelationfunctionalasanexample,bothver- functional theory that addressed non-equilibrium sedimenta-
sionsareidentical: tion of colloids [138], the self-diffusion of particles in com-
| ˆ   | ˆ   |     |     | ˆ ˆ |     |     |     | plexfluids[139],andthebehaviourofthevanHovetwo-body |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --------------------------------------------------- | --- | --- | --- | --- | --- | --- |
|     | 1   |     |     | 1   |     |     |     |                                                     |     |     |     |     |     |     |
dynamicsofcolloidalBrownianharddisks[140]andofhard
| drρ(r)     |            | dac (r,[ρ | ])=     | da       | drρ(r)c  | (r,[ρ | ]).     |                   |         |             |            |            |          |             |
| ---------- | ---------- | --------- | ------- | -------- | -------- | ----- | ------- | ----------------- | ------- | ----------- | ---------- | ---------- | -------- | ----------- |
|            |            | 1         | a       |          |          | 1     | a       |                   |         |             |            |            |          |             |
|            | 0          |           |         | 0        |          |       |         | spheres[141,142]. |         |             |            |            |          |             |
|            |            |           |         |          |          |       | (57)    | Several           | current | statistical | mechanical |            | research | threads are |
|            |            |           |         |          |          |       |         | dedicated         | to the  | force       | point of   | view. This | includes | novel       |
| Our (mild) | preference |           | for the | order on | the left | hand  | side of |                   |         |             |            |            |          |             |
force-samplingtechniquesthatsignificantlyreducetheseem-
| equation  | (57) has    | two | reasons.  | (i) In       | a numerical |          | scheme, |                |                |      |          |           |            |           |
| --------- | ----------- | --- | --------- | ------------ | ----------- | -------- | ------- | -------------- | -------------- | ---- | -------- | --------- | ---------- | --------- |
|           |             |     |           |              |             |          |         | ingly inherent | statistical    |      | noise in | many-body | simulation | res-      |
| where one | discretizes |     | on a grid | of positions |             | r and of | values  |                |                |      |          |           |            |           |
|           |             |     |           |              |             |          |         | ults for       | key quantities | such | as the   | density   | profile    | [110–112, |
ofa,themultiplicationbyρ(r)isonlyrequiredtobecarried
|     |     |     |     |     |     |     |     | 143]. The | statistical | Noether | invariance | theory |     | [90–98] gen- |
| --- | --- | --- | --- | --- | --- | --- | --- | --------- | ----------- | ------- | ---------- | ------ | --- | ------------ |
outonceateachgridpointr,whenusingthelefthandside,not
eratesformalexpressionsforforcecorrelationfunctionsvery
alsoforeveryvalueofaasonth´erighthandside.(ii)Although
|     |     |     |     |         |                 |     |     | naturally. | Corresponding |     | exact sum | rules | interrelate | correl- |
| --- | --- | --- | --- | ------- | --------------- | --- | --- | ---------- | ------------- | --- | --------- | ----- | ----------- | ------- |
|     |     |     |     | 1 (r,[ρ | ]),dependsonthe |     |     |            |               |     |           |       |             |         |
theresultoftheinnerintegral, dac 1 a ations that involve forces, force gradients, and more gen-
0
| specificchosenparameterizationρ |     |     |     | (r)andishencenotunique |     |     |     |                                                       |     |     |     |     |     |     |
| ------------------------------- | --- | --- | --- | ---------------------- | --- | --- | --- | ----------------------------------------------------- | --- | --- | --- | --- | --- | --- |
|                                 |     |     |     | a                      |     |     |     | eralobservablesinahyperforceframework[97].Force-based |     |     |     |     |     |     |
fromtheviewpointoftheentirefunctional,itneverthelesscon-
densityfunctionalapproacheswereputforwardbothquantum
| stitutesawell-definedlocalizedfunctionof |     |     |     |     | r.  |     |     |     |     |     |     |     |     |     |
| ---------------------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
mechanically[144–148]andclassically[93,94].
Wehavebrieflytouchedontheconceptofforceswhendis-
cussingthedirectcorrelationsumrule(48).Locallyresolved
4. Nonequilibriumdynamics
|     |     |     |     |     |     |     |     | force fields | are | central | to power | functional | theory | [9, 149– |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------ | --- | ------- | -------- | ---------- | ------ | -------- |
We have so far demonstrated that the equilibrium properties 151] for the description of the nonequilibrium dynamics of
ofcorrelatedmany-bodysystemscanbeinvestigatedonavery underlyingmany-bodysystems.Theconnectiontothepresent
deeplevelbyusingneuralnetworkstorepresentthefunctional frameworkisviathelocallyresolvedinterparticleforcedens-
relationship that are inherent in the statistical physics. The ity F (r,t). When expressed in correlator form, this vector
int
required computational workload is thereby only quite mod- fieldisgivenasthefollowingnonequilibriumaverage:
erate. The neural functionals that encapsulate the nontrivial DX (cid:1)E
(cid:0)
informationaboutcorrelationsandaboutthermodynamicsare F (r,t)=− δ(r − r)∇ u rN . (58)
|              |     |      |        |             |             |     |        |     | int |     |     | i   | i   |     |
| ------------ | --- | ---- | ------ | ----------- | ----------- | --- | ------ | --- | --- | --- | --- | --- | --- | --- |
| lean, robust | and | they | can be | manipulated | efficiently |     | by the |     |     |     |     |     |     |     |
i
neuralfunctionalcalculusoutlinedabove.
These features of the neural theory naturally lead one The dependence on time t arises as the average on the right
to wonder about the potential applicability beyond equilib- hand side of equation (58), which is taken over the instant-
rium,i.e.tosituationswheretheconsideredsystemisdriven aneousnonequilibriummany-bodyprobabilitydistribution,as
by external forces such that flow is generated. The recent given by temporal evolution of the Smoluchowski equation
nonequilibrium machine-learning method by de las Heras forthecaseofoverdampeddynamics.Theinterparticleforce
et al [40] is based on the dynamical one-body force balance densityF (r,t)canbesplitintoasumofanequilibrium-like
int
relationship for overdamped Brownian motion. The required ‘adiabatic’ force density F (r,t) and a genuine nonequilib-
ad
(r,t).Makingthefunc-
dynamicalfunctionaldependenciesarethosegivenbypower rium‘superadiabatic’contributionF sup
functionaltheory[9].Thepowerfunctionalapproachisform- tionaldependenciesexplicit,astheyariseinpowerfunctional
ally exact and it goes beyond dynamical density functional theory[9],givesthefollowingsumoftwocontributions:
theory[5,69,118,131–133]inthatitalsocapturesnonequi-
librium interparticle force contributions that exceed those F (r,t,[ρ,v])=F (r,t,[ρ])+F (r,t,[ρ,v]). (59)
|           |        |      |        |             |     |          |      | int |     | ad  |     | sup |     |     |
| --------- | ------ | ---- | ------ | ----------- | --- | -------- | ---- | --- | --- | --- | --- | --- | --- | --- |
| generated | by the | free | energy | functional; | see | [9, 119, | 120, |     |     |     |     |     |     |     |
134]forrecentreviews.Suchgenuinenonequilibriumeffects Here the functional arguments are the density profile ρ(r,t)
includeviscousandstructuralnonequilibriumforcefields[9, andtheone-bodyvelocityfieldv(r,t)=J(r,t)/ρ(r,t),which
135–137], which for uniaxial compressional flow of a three- are both microscopically resolved in space and in time. The
dimensional Lennard–Jones fluid were shown to be well- numerator is the one-body current, which is givPen as an
|     |     |     |     |     |     |     |     | instantaneousnonequilibriumaverageviaJ(r,t)=⟨ |     |     |     |     |     | δ(r − |
| --- | --- | --- | --- | --- | --- | --- | --- | --------------------------------------------- | --- | --- | --- | --- | --- | ----- |
representedbyatrainedneuralnetwork[40].
|     |     |     |     |     |     |     |     | ⟩   |     |     |     |     |     | i   |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
The neural nonequilibrium force fields were successfully r)v ,wherev(rN,t)isthevelocityofparticleiintheunder-
|     |     |     |     |     |     |     |     | i i | i   |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
comparedagainstanalyticalpowerfunctionalapproximations, lyingmany-bodyoverdampedBrowniandynamics.
where simple and physically motivated semi-local depend- De las Heras et al [40] present a demonstration of the
ence on both the local density and local velocity gradients validityofthefunctionaldependenceonρ(r,t)andv(r,t)via
17

| J.Phys.:Condens.Matter36(2024)243002 |     |     |     |     |     |     |     |     |     |     | TopicalReview |     |
| ------------------------------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ------------- | --- |
successfulmachine-learningofF (r,t,[ρ,v])forinhomogen- 5. Conclusionsandoutlook
int
eousnonequilibriumsteadystates.Thestrategyforconstruct-
ing the neural network is similar to that described here, but Inconclusionwehavegivenadetailedaccountoftherecent
|             |               |     |             |     |          |                |     | neural functional | theory | [41] for the structure | and | thermo- |
| ----------- | ------------- | --- | ----------- | --- | -------- | -------------- | --- | ----------------- | ------ | ---------------------- | --- | ------- |
| it is based | on predicting |     | the locally |     | resolved | nonequilibrium |     |                   |        |                        |     |         |
forcesratherthantheequilibriumone-bodydirectcorrelations. dynamics of spatially inhomogeneous classical many-body
Oneimportantconnectionbetweenequilibriumandnonequi- systems. The approach is based on input data obtained from
librium is given by the adiabatic construction [9] that relates Monte Carlo simulations that provide results for averaged
F (r,t,[ρ])inthenonequilibriumsystemtoaninstantaneous densityprofiles.Therebythetrainingsystemsareexposedto
ad
|             |        |      |           |         |         | ρ(r,t). |     | theinfluenceofrandomizedexternalpotentials.Basedonthe |     |     |     |     |
| ----------- | ------ | ---- | --------- | ------- | ------- | ------- | --- | ----------------------------------------------------- | --- | --- | --- | --- |
| equilibrium | system | with | identical | density | profile |         | The |                                                       |     |     |     |     |
adiabatic force field is then given as a density functional via functionalrelationshipsthatarerigorouslygivenbyclassical
thestandardrelationship densityfunctionaltheory,thetrainingdataisusedtoconstruct
aneuralnetworkrepresentationoftheone-bodydirectcorrel-
Tρ(r,t)∇ ationfunctional,whichactsasafundamental‘mother’object
|     | F ad | (r,t,[ρ])=k | B   |     | c 1 (r,[ρ]), |     | (60) |     |     |     |     |     |
| --- | ---- | ----------- | --- | --- | ------------ | --- | ---- | --- | --- | --- | --- | --- |
intheneuralfunctionaltheory.
Fromautomaticfunctionaldifferentiationoftheone-body
wherethedensityargumentoftheone-bodydirectcorrelation
directcorrelationfunctionalfollowdaughterandgranddaugh-
| functional | c (r,[ρ]) | is  | the instantaneous |     | density | distribution |     |     |     |     |     |     |
| ---------- | --------- | --- | ----------------- | --- | ------- | ------------ | --- | --- | --- | --- | --- | --- |
1
|     |     |     |     |     |     |     |     | ter functionals | that represent | two- and three-body |     | direct cor- |
| --- | --- | --- | --- | --- | --- | --- | --- | --------------- | -------------- | ------------------- | --- | ----------- |
ρ(r,t).
relationfunctionals.Conversely,functionalintegrationyields
ForoverdampedBrowniandynamicswithfrictionconstant
theneuralexcessfreeenergyfunctional,whichactsastheulti-
γ,theone-bodycurrentJ(r,t)appearsintheforcedensitybal-
mategrandmotherfunctionalinthegenealogy.Wehaveshown
ance,whichisgivenby
thatchainingtogetherthefunctionaldifferentiationandinteg-
|           |     |             |     |               |     |        |      | ration operations | yields | exact functional | sum rules. | Further |
| --------- | --- | ----------- | --- | ------------- | --- | ------ | ---- | ----------------- | ------ | ---------------- | ---------- | ------- |
| γJ(r,t)=− | k   | T ∇ρ(r,t)+F |     | (r,t)+ρ(r,t)f |     | (r,t), | (61) |                   |        |                  |            |         |
B int ext exactidentitiesaregivenbythestatisticalmechanicalNoether
|     |     |     |     |     |     |     |     | invariance | theory [90–98], | by variety of fundamental |     | liquid |
| --- | --- | --- | --- | --- | --- | --- | --- | ---------- | --------------- | ------------------------- | --- | ------ |
(r,t)
where f ext is an external force field that acts on the state techniques [8, 20–23] and by functional calculus alone
system, in general in a time- and position-dependent fash- [5, 7]. We have described a selection of these sum rules in
ion. The prescription for the current is complemented by the detailandhaveshownhowtheirvaliditycanbeusedtocarry
microscopically resolved continuity equation, ∂ρ(r,t)/∂t= outconsistencyandaccuracychecksforthedifferentlevelsof
−∇· J(r,t). Upon neglecting the superadiabatic force dens- mutuallyrelatedneuraldensityfunctionals.
ity in equation (59) and hence only taking adiabatic forces Wehavehereinparticularfocusedontheone-dimensional
intoaccount,i.e.approximatingF (r,t,[ρ,v])≈ F (r,t,[ρ]), hard rod systems for reasons of ease of data generation via
|     |     |     |     | int |     | ad  |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
onearrivesatthedynamicaldensityfunctionaltheory[5,69, simulations [42], the availability of Percus’ exact functional
118]. Its inherent central approximation is hence to replace [55],thepossibilityofanalyticalmanipulationstobecarried
thenonequilibriumforcesbyeffectiveequilibriumforcesthat out, and not least the fundamental character of this classical
areobtainedfromthefreeenergyfunctionalviatheadiabatic model [54]. A beginner-friendly interactive code tutorial is
construction[9]. providedonline[42],togetherwithstand-alonedocumentation
Returningtotheone-dimensionalgeometryofthehardrod thatdescribesthekeystrategiesandtheessenceofthemeth-
model,thisleadstothefollowingclosedapproximateequation odsthatconstitutetheneuralfunctionaltheory[41].Wehave
ofmotionforthetime-dependentdensityprofile: discussedprototypicalapplicationsfor‘simulationbeyondthe
box’,wheretheneuralfunctionalisusedforsystemsizesthat
∂ρ(x,t) outscale the dimension of the original training box that was
|     | =D ∇[∇ρ(x,t)−ρ(x,t)(∇c |     |     |     | (x,[ρ])+βfext |     | (x,t))]. |                  |                |                   |           |          |
| --- | ---------------------- | --- | --- | --- | ------------- | --- | -------- | ---------------- | -------------- | ----------------- | --------- | -------- |
|     | 0                      |     |     |     | 1             |     |          |                  |                |                   |           |          |
| ∂t  |                        |     |     |     |               |     |          | used to generate | the underlying | Monte Carlo       | data      | [41]. We |
|     |                        |     |     |     |               |     | (62)     | have also given  | an overview    | of nonequilibrium | methods   | and      |
|     |                        |     |     |     |               |     |          | have emphasized  | the important  | role of the       | occurring | force    |
∇=∂/∂xinonedimensionandthe
| Thederivativeissimply |     |     |     |     |     |     |     | fieldsandtheirfunctionaldependencies. |     |     |     |     |
| --------------------- | --- | --- | --- | --- | --- | --- | --- | ------------------------------------- | --- | --- | --- | --- |
diffusion constant D =k T/γ is the ratio of thermal energy We recall that a detailed description of the setup of the
0 B
and the friction constant. Equation (62) can be efficiently paper is given before the start of section 1.1; the modular
propagated in time with a simple forward Euler algorithm structure of the paper invites for selective reading. An over-
andtheneuralrepresentationofc (x,[ρ])canbeusedinlieu viewoftherelevantstatisticalmechanicalconceptsisgivenin
1
ofananalyticapproximation.Howeversuperadiabaticforces, section 1. The neural functional theory is described in detail
i.e.forcecontributionsthatgobeyondtheadiabaticapproxim- insection2andwehaveemphasizedtheimportantconceptof
ationofworkingwithafreeenergyfunctional,areneglected. locallearning,asillustratedinfigure2,whichfacilitatesvery
Theseincludeviscousandstructuralnonequilibriumcontribu- efficient network construction and training. The neural func-
tions; we refer the Reader to [9] for background and to [40] tional approach allows to explicitly carry out functional cal-
for a recent perspective on the description of microscopic culusaspresentedinsection3anditisrelevantfornonequi-
nonequilibrium dynamics of fluids in the light of machine libriumasdescribedinsection4.Weoncemorehighlightthe
learningonthebasisofpowerfunctionaltheory. availability of the online tutorial [42], which covers all key
18

J.Phys.:Condens.Matter36(2024)243002 TopicalReview
aspects of our study and includes a practitioner’s account of This leaves over the question of the status of analytical
automaticdifferentiationanddifferentiableprogramming. density functionals in the light of the neural network cap-
The neural functional theory is a genuine hybrid method abilities. We have here deliberately chosen the exact Percus
that draws with comparable weight from computer simula- functionalforone-dimensionalhardrodstodemonstratehow
tions, machine learning, and density functional theory. The much insight can be gleaned from the analytical manipula-
compuational and conceptual complexities of the involved tions;asarepresentativeexampleseethenonlinearconvolu-
methodsfromeachrespectivefieldarerelativelylow.Yettheir tionalstructureofequations(24)–(28)alongwiththeexcellent
combinationoffersanewandarguablyunprecedentedviewof numericalcomparisonagainsttheneuralfunctionalasshown
thestatisticalphysicsofmany-bodysystems.Welayoutinthe infigure7(b).Astheneuralfunctionalmethodisnotrestricted
followingwhytheapproachisinterestingfromtheviewpoints tothehardcoresystem,onecanexpectthathavinganaccurate
ofeachofthethreeconstituentapproaches. neuralfunctionalforagivensystemcanbeofverysignificant
Fromthemachine-learningperspectiveitseemsunusualto help when attempting first-principles construction of analyt-
have a large set of testable self-consistency conditions avail- icalfreeenergyfunctionals.Afterallweshouldmakeuseof
able. These conditions stem from statistical mechanical sum thetoolsthatvanderWaalsdidnothaveathisdisposal!
rules, as they follow e.g. from the Noether invariance the- Insummary,inlightoftheprogressreportedin[40,41]and
ory, the functional integration-differentiation structure, and the present model investigation, we anticipate that a wealth
exchange symmetry. Taking the latter case as an example, ofdeepquestionscanbeaddressedfromtheviewpointofthe
thattheautomaticderivativeofaneuralnetworksatisfiesthe neural functional theory, including fundamental questions of
exchange symmetry of its two (position) arguments is very phasecoexistence[154]aswellasthepossibleconstructionof
remarkable, see the graphical demonstration of the diagonal fundamental measure functionals [155, 156]. While we here
symmetry in figure 7(c). This is a purely structural test for have restricted ourselves to hard core systems, the principal
thequalityofthenetworkthatdoesnotrequireanyindepend- applicabilityoftheneuralfunctionaltheoryforsoftpotentials
ent reference data as a benchmark. All presented sum rules wasdemonstratedin[41]for(planar)inhomogeneitiesofthe
are of this type and they hence provide intrinsic constraints, supercritical three-dimensional Lennard–Jones fluid. Going
either genuinely following from the underlying Statistical beyond planar geometry and addressing spatial inhomogen-
Mechanics or from mere functional calculus alone, which is eityintwoorthreedimensionscouldbenefitfromtheuseof
the case for the functional integration-differentiation formal- equivariantneuralnetworks[157–163],whichpossessthefun-
ismoutlinedinsection3.4.Crucially,inourmethodologythe damentalsymmetrypropertiesofEuclideanspace.
constraintsarenotenforcedduringtrainingthenetwork,asis For complex Hamiltonians the required amount of simu-
doneinmethodsofphysics-informedmachinelearninginthe lation work to provide training data might seem as a lim-
classicaldensityfunctional[37]andwider[152,153]contexts. itation. We are however optimistic that the subsequent effi-
Fromacomputersimulationpointofviewtheneuralfunc- cient use of the direct correlation functionals in the form of
tionalmethodsofferanewwayofdesigningsimulationwork. neuralnetworkscanbyfaroutweighthetrainingcost.Hence
Instead of direct simulation of the physical problem at hand, the application to complex models such as the monatomic
aninterveningstepofconstructingthedirectcorrelationfunc- Molinero-Moorewatermodel[164,165]mightnotbeoutof
tionalisintroduced.Wehaveshownthatthedirectcorrelation reach. Furthermore it is inspiring to think that potential pro-
functional can thereby be obtained explicitly and accurately. gress could be made in the treatment of dielectric [166] and
Rather than playing the role of a formal object, its availabil- long-rangedforces[167].
ityasatrainedneuralnetworkfacilitatesmakingfastandpre- As a final note, we re-emphasize the successful applica-
cisepredictionsinnontrivialsituations.Thisapplicationstage tion of the neural method to nonequilibrium flow problems
oftheneuralfunctionaltheoryrequiresverylittleeffortboth presentedin[40]anditiscertainlyveryinspiringtospeculate
in terms of the required numerical algorithmic structure and whetherthisfacilitatesmakingprogressconcerningquestions
the computational workload; we recall the illustration of the of slow dynamics in soft matter [153, 168, 169] and beyond
neuralfunctionalworkflowshowninfigure4. that[170].
Fromadensityfunctionalperspectivetheneuralapproach
isarguablyunprecedentedinitsdegreeofaccesstotheexcess
Dataavailabilitystatement
free energy functional. We find it highly remarkable that so
much of the seemingly very abstract functional relationships
The data and code that support the findings of this study are
andformalconceptscanbeinspectedandtestedincomputa-
openly available at the following URL: https://github.com/
tionallystraightforwardandhighlyefficientways.Therange
sfalmo/NeuralDFT-Tutorial[42].
ofthesemethodsincludesautomaticdifferentiationtogener-
ate direct correlation functions as well as performant func-
tional integration routines. The neural functional framework Acknowledgments
offersthepossibilitytoworknumericallywithexactfunctional
identities with great ease. Hence the neural network techno- We thank Daniel de las Heras and Bob Evans for useful dis-
logyrelievesonefromthetaskofconstructinganapproximate cussionsandtheorganizersandparticipantsofHISML2023
analyticalfunctionalandmanipulatingitonpaper. [170] for inspiring feedback throughout the workshop. This
19

J.Phys.:Condens.Matter36(2024)243002 TopicalReview
workissupportedbytheGermanResearchFoundation(DFG) [18] Hernández-Mu˜nozJ,ChacónEandTarazonaP2019Density
viaProjectNo.436306241. functionalanalysisofatomicforcemicroscopyinadense
fluidJ.Chem.Phys.151034701
[19] CatsP,EvansR,HärtelAandvanRoijR2021Primitive
modelelectrolytesinthenearandfarfield:decaylengths
ORCIDiDs
fromDFTandsimulationsJ.Chem.Phys.154124504
[20] BausM1984Brokensymmetryandinvariancepropertiesof
FlorianSammüllerhttps://orcid.org/0000-0002-3605-
classicalfluidsMol.Phys.51211
329X [21] EvansRandParryAO1990Liquidsatinterfaces:whatcan
SophieHermannhttps://orcid.org/0000-0002-4012-9170 atheoristcontribute?J.Phys.:Condens.Matter2SA15
MatthiasSchmidthttps://orcid.org/0000-0002-5015-2972 [22] HendersonJR1992Statisticalmechanicalsumrules
FundamentalsofInhomogeneousFluidsedDHenderson
(Dekker)ch2
[23] UptonPJ1998Fluidsagainsthardwallsandsurfacecritical
References behaviorPhys.Rev.Lett.812300
[24] CleggPS2021Characterisingsoftmatterusingmachine
[1] vanderWaalsJD1894ThermodynamischeTheorieder learningSoftMatter173991
KapillaritätunterVoraussetzungstetigerDichteänderung [25] DijkstraMandLuijtenE2021Frompredictivemodellingto
(Thermodynamictheoryofcapillarityunderthe machinelearningandreverseengineeringofcolloidal
hypothesisofacontinuousvariationofdensity)Z.Phys. self-assemblyNat.Mater.20762
Chem.13U657RowlinsonJS1979J.Stat.Phys.20197 [26] BoattiniE,DijkstraMandFilionL2019Unsupervised
(Engl.transl.) learningforlocalstructuredetectionincolloidalsystems
[2] RowlinsonJSandWidomB2002MolecularTheoryof J.Chem.Phys.151154901
Capillarity(Dover) [27] Campos-VillalobosG,BoattiniE,FilionLandDijkstraM
[3] HohenbergPandKohnW1964Inhomogeneouselectrongas 2021Machinelearningmany-bodypotentialsforcolloidal
Phys.Rev.136B864 systemsJ.Chem.Phys.155174902
[4] MerminND1965Thermalpropertiesoftheinhomogeneous [28] Campos-VillalobosG,GiuntaG,Marín-AguilarSand
electrongasPhys.Rev.137A1441 DijkstraM2022Machine-learningeffectivemany-body
[5] EvansR1979Thenatureoftheliquid-vapourinterfaceand potentialsforanisotropicparticlesusing
othertopicsinthestatisticalmechanicsofnon-uniform, orientation-dependentsymmetryfunctionsJ.Chem.Phys.
classicalfluidsAdv.Phys.28143 157024902
[6] EvansR,OettelM,RothRandKahlG2016New [29] RodriguesFA2023Machinelearninginphysics:ashort
developmentsinclassicaldensityfunctionaltheoryJ. guideEurophys.Lett.14422001
Phys.:Condens.Matter28240401 [30] WuJandGuM2023Perfectingliquid-statetheorieswith
[7] EvansR1992Densityfunctionalsinthetheoryof machineintelligenceJ.Phys.Chem.Lett.1410545
nonuniformfluidsFundamentalsofInhomogeneous [31] Santos-SilvaT,TeixeiraPIC,Anquetil-DeckCand
FluidsedDHenderson(Dekker)ch3 CleaverDJ2014Neural-networkapproachtomodeling
[8] HansenJPandMcDonaldIR2013TheoryofSimple liquidcrystalsincomplexconfinementPhys.Rev.E
Liquids4thedn(Academic) 89053316
[9] SchmidtM2022Powerfunctionaltheoryformany-body [32] Shang-ChunLandOettelM2019Aclassicaldensity
dynamicsRev.Mod.Phys.94015007 functionalfrommachinelearningandaconvolutional
[10] KohnWandShamLJ1965Self-consistentequations neuralnetworkSciPostPhys.6025
includingexchangeandcorrelationeffectsPhys.Rev. [33] LinS-C,MartiusGandOettelM2020Analyticalclassical
140A1133 densityfunctionalsfromanequationlearningnetworkJ.
[11] KohnW1999Nobellecture:electronicstructureof Chem.Phys.152021102
matter–wavefunctionsanddensityfunctionalsRev.Mod. [34] CatsP,KuipersS,deWindS,vanDammeR,ColiGM,
Phys.711253 DijkstraMandvanRoijR2021Machine-learning
[12] EvansR,FrenkelDandDijkstraM2019Fromsimpleliquids free-energyfunctionalsusingdensityprofilesfrom
tocolloidsandsoftmatterPhys.Today7238 simulationsAPLMater.9031109
[13] LevesqueM,VuilleumierRandBorgisD2012Scalar [35] QiaoC,YuX,SongX,ZhaoT,XuX,ZhaoSand
fundamentalmeasuretheoryforhardspheresinthree GubbinsKE2020Enhancinggassolubilityinnanopores:
dimensions:applicationtohydrophobicsolvationJ.Chem. acombinedstudyusingclassicaldensityfunctionaltheory
Phys.137034115 andmachinelearningLangmuir368527
[14] EvansR,StewartMCandWildingNB2019Aunified [36] YatsyshinP,KalliadasisSandDuncanAB2022
descriptionofhydrophilicandsuperhydrophobicsurfaces Physics-constrainedBayesianinferenceofstatefunctions
intermsofthewettinganddryingtransitionsofliquids inclassicaldensity-functionaltheoryJ.Chem.Phys.
Proc.NatlAcad.Sci.11623901 156074105
[15] CoeMK,EvansRandWildingNB2022Densitydepletion [37] Malpica-MoralesA,YatsyshinP,Duran-OlivenciaMAand
andenhancedfluctuationsinwaternearhydrophobic KalliadasisS2023Physics-informedBayesianinference
solutes:identifyingtheunderlyingphysicsPhys.Rev.Lett. ofexternalpotentialsinclassicaldensityfunctionaltheory
128045501 J.Chem.Phys.159104109
[16] JeanmairetG,LevesqueMandBorgisD2013Molecular [38] FangX,GuMandWuJ2022Reliableemulationofcomplex
densityfunctionaltheoryofwaterdescribing functionalsbyactivelearningwitherrorcontrolJ.Chem.
hydrophobicityatshortandlonglengthscalesJ.Chem. Phys.157214109
Phys.139154101 [39] SimonA,WeimarJ,MartiusGandOettelM2024Machine
[17] Martin-JimenezD,ChacónE,TarazonaPandGarciaR2016 learningofadensityfunctionalforanisotropicpatchy
Atomicallyresolvedthree-dimensionalstructuresof particlesJ.Chem.TheoryComput.201062
electrolyteaqueoussolutionsnearasolidsurfaceNat. [40] delasHerasD,ZimmermannT,SammüllerF,HermannS
Commun.712164 andSchmidtM2023Perspective:Howtoovercome
20

J.Phys.:Condens.Matter36(2024)243002 TopicalReview
dynamicaldensityfunctionaltheoryJ.Phys.:Condens. [61] RosenfeldY1989Free-energymodelfortheinhomogeneous
Matter35271501 hard-spherefluidmixtureanddensity-functionaltheoryof
[41] SammüllerF,HermannS,delasHerasDandSchmidtM freezingPhys.Rev.Lett.63980
2023Neuralfunctionaltheoryforinhomogeneousfluids: [62] TarazonaP2000Densityfunctionalforhardspherecrystals:
fundamentalsandapplicationsProc.NatlAcad.Sci. afundamentalmeasureapproachPhys.Rev.Lett.84694
120e2312484120 [63] RothR,EvansR,LangAandKahlG2002Fundamental
[42] SammüllerF2023Neuralfunctionaltheoryfor measuretheoryforhard-spheremixturesrevisited:the
inhomogeneousfluids—tutorial(availableat:https:// WhiteBearversionJ.Phys.:Condens.Matter1412063
github.com/sfalmo/NeuralDFT-Tutorial) [64] Hansen-GoosHandRothR2006Densityfunctionaltheory
[43] NagaiR,AkashiR,SasakiSandTsuneyukiS2018 forhard-spheremixtures:theWhiteBearversionmarkII
Neural-networkKohn-Shamexchange-correlation J.Phys.:Condens.Matter188413
potentialanditsout-of-trainingtransferabilityJ.Chem. [65] RothR2010Fundamentalmeasuretheoryforhard-sphere
Phys.148241737 mixtures:areviewJ.Phys.:Condens.Matter22063102
[44] SchmidtJ,Benavides-RiverosCLandMarquesMAL2019 [66] KierlikEandRosinbergML1990Free-energydensity
Machinelearningthephysicalnonlocal functionalfortheinhomogeneoushard-spherefluid:
exchange-correlationfunctionalofdensity-functional applicationtointerfacialadsorptionPhys.Rev.A423382
theoryJ.Phys.Chem.Lett.106425 [67] KierlikEandRosinbergML1991Density-functionaltheory
[45] ZhouY,WuJ,ChenSandChenG2019Towardtheexact forinhomogeneousfluids:adsorptionofbinarymixtures
exchange-correlationpotential:athree-dimensional Phys.Rev.A445025
convolutionalneuralnetworkconstructJ.Phys.Chem. [68] PhanS,KierlikE,RosinbergML,BildsteinBandKahlG
Lett.107264 1993Equivalenceoftwofree-energymodelsforthe
[46] NagaiR,AkashiRandSuginoO2020Completingdensity inhomogeneoushard-spherefluidPhys.Rev.E48618
functionaltheorybymachinelearninghiddenmessages [69] MarconiUMBandTarazonaP1999Dynamicdensity
frommoleculesnpjComput.Mater.643 functionaltheoryoffluidsJ.Chem.Phys.1108032
[47] LiL,HoyerS,PedersonR,SunR,CubukED,RileyPand [70] LipsD,RyabovAandMaassP2018Brownianasymmetric
BurkeK2021Kohn-Shamequationsasregularizer: simpleexclusionprocessPhys.Rev.Lett.121160601
buildingpriorknowledgeintomachine-learnedphysics [71] LipsD,RyabovAandMaassP2019Single-filetransportin
Phys.Rev.Lett.126036401 periodicpotentials:theBrownianasymmetricsimple
[48] LiH,WangZ,ZouN,YeM,XuR,GongX,DuanWand exclusionprocessPhys.Rev.E100052121
XuY2022Deep-learningdensityfunctionaltheory [72] LipsD,RyabovAandMaassP2020Nonequilibrium
Hamiltonianforefficientabinitioelectronic-structure transportandphasetransitionsindrivendiffusionof
calculationNat.Comput.Sci.2367 interactingparticlesZ.Naturforsch.A75449
[49] GedeonJ,SchmidtJ,HodgsonMJP,WetherellJ, [73] AntonovAP,RyabovAandMaassP2022Solitonsin
Benavides-RiverosCLandMarquesMAL2022 overdampedBrowniandynamicsPhys.Rev.Lett.
Machinelearningthederivativediscontinuityof 129080601
density-functionaltheoryMach.Learn.:Sci.Technol. [74] SchmidF2022Editorial:Multiscalesimulationmethods
3015011 forsoftmattersystemsJ.Phys.:Condens.Matter
[50] PedersonR,KalitaBandBurkeK2022Machinelearning 34160401
anddensityfunctionaltheoryNat.Rev.Phys.4357 [75] BaptistaLA,DuttaRC,SevillaM,HeidariM,PotestioR,
[51] HuangB,vonRudorffGFandvonLilienfeldOA2023The KremerKandCortes-HuertoR2021
centralroleofdensityfunctionaltheoryintheAIage Density-functional-theoryapproachtotheHamiltonian
Science381170 adaptiveresolutionsimulationmethodJ.Phys.:Condens.
[52] SantosA,YusteSBanddeHaroML2020Structuraland Matter33184003
thermodynamicpropertiesofhard-spherefluidsJ.Chem. [76] GholamiA,HöflingF,KleinRandDelleSiteL2021
Phys.153120901 Thermodynamicrelationsatthecouplingboundaryin
[53] RoyallCP,CharbonneauP,DijkstraM,RussoJ, adaptiveresolutionsimulationsforopensystemsAdv.
SmallenburgF,SpeckTandValerianiC2023Colloidal TheorySimul.42000303
hardspheres:triumphs,challengesandmysteries [77] YagiTandSatoH2021Self-consistentconstructionof
(arXiv:2305.02452) bridgefunctionalbasedontheweighteddensity
[54] TonksL1936Thecompleteequationofstateofone-,two- approximationJ.Chem.Phys.154124113
andthree-dimensionalgasesofhardelasticspheresPhys. [78] YagiTandSatoH2022Self-consistentconstructionofgrand
Rev.50955 potentialfunctionalwithhierarchicalintegralequations
[55] PercusJK1976Equilibriumstateofaclassicalfluidofhard anditsapplicationtosolvationthermodynamicsJ.Chem.
rodsinanexternalfieldJ.Stat.Phys.15505 Phys.156054116
[56] RobledoAandVareaC1981Ontherelationshipbetweenthe [79] IsoSandKawanaK2019Densityrenormalization
densityfunctionalformalismandthepotentialdistribution groupforclassicalliquidsProg.Theor.Exp.Phys.
theoryfornonuniformfluidsJ.Stat.Phys.26513 2019013A01
[57] VanderlickTK,DavisHTandPercusJK1989The [80] YokotaT,HaruyamamJandSuginoO2021
statisticalmechanicsofinhomogeneoushardrodmixtures Functional-renormalization-groupapproachtoclassical
J.Chem.Phys.917136 liquidswithshort-rangerepulsion:aschemewithout
[58] BakhtiB,SchottSandMaassP2012Exactdensity repulsivereferencesystemPhys.Rev.E104014124
functionalforhard-rodmixturesderivedfromMarkov [81] KawanaK2023Noteongeneralfunctionalflowsin
chainapproachPhys.Rev.E85042107 equilibriumsystems(arXiv:2309.10496)
[59] PercusJK2013Arandomwalktofundamentalmeasure [82] SchmidtM1999Density-functionaltheoryforsoftpotentials
theory—amini-reviewatapersonallevelJ.Stat.Phys. bydimensionalcrossoverPhys.Rev.E60R6291
150601 [83] SchmidtM2000Adensityfunctionalforadditivemixtures
[60] RosenfeldY1988Scaledfieldparticletheoryofthestructure Phys.Rev.E623799
andthethermodynamicsofisotropichardparticlefluidsJ. [84] SchmidtM2000Fluidstructurefromdensityfunctional
Chem.Phys.894272 theoryPhys.Rev.E624976
21

J.Phys.:Condens.Matter36(2024)243002 TopicalReview
[85] PercusJK1982One-dimensionalclassicalfluidwith [109] BrukhnoAV,GrantJ,UnderwoodTL,StratfordK,
nearest-neighborinteractioninarbitraryexternalfieldJ. ParkerSC,PurtonJAandWildingNB2021
Stat.Phys.2867 DL_MONTE:amultipurposecodeforMonteCarlo
[86] BuschleJ,MaassPandDieterichW2000Exactdensity simulationMol.Simul.47131
functionalsinonedimensionJ.Phys.A:Math.Gen. [110] BorgisD,AssarafR,RotenbergBandVuilleumierR2013
33L41 Computationofpairdistributionfunctionsand
[87] LikosCNandAshcroftNW1992Self-consistenttheoryof three-dimensionaldensitieswithareducedvariance
freezingoftheclassicalone-componentplasmaPhys.Rev. principleMol.Phys.1113486
Lett.69316 [111] delasHerasDandSchmidtM2018Betterthancounting:
[88] LikosCNandAshcroftNW1993Density-functionaltheory densityprofilesfromforcesamplingPhys.Rev.Lett.
ofnonuniformclassicalliquids:anextendedmodified 120218001
weighted-densityapproximationJ.Chem.Phys.999090 [112] RotenbergB2020Usetheforce!Reducedvariance
[89] KolafaJ,LabíkSandMalijevsk´yA2004Accurateequation estimatorsfordensities,radialdistributionfunctionsand
ofstateofthehardspherefluidinstableandmetastable localmobilitiesinmolecularsimulationsJ.Chem.Phys.
regionsPhys.Chem.Chem.Phys.62335 153150902
[90] HermannSandSchmidtM2021Noether’stheoremin [113] JexM,LewinMandMadsenP2023Classicaldensity
statisticalmechanicsCommun.Phys.4176 functionaltheory:thelocaldensityapproximation
[91] HermannSandSchmidtM2022WhyNoether’stheorem (arXiv:2310.18028)
appliestostatisticalmechanicsJ.Phys.:Condens.Matter [114] delasHerasDandSchmidtM2015Sedimentationstacking
34213001 diagramofbinarycolloidalmixturesandbulkphasesin
[92] HermannSandSchmidtM2022Varianceoffluctuations theplaneofchemicalpotentialsJ.Phys.:Condens.Matter
fromNoetherinvarianceCommun.Phys.5276 27194115
[93] TschoppSM,SammüllerF,HermannS,SchmidtMand [115] EckertT,SchmidtManddelasHerasD2021
BraderJM2022Forcedensityfunctionaltheoryin-and Gravity-inducedphasephenomenainplate-rodcolloidal
out-of-equilibriumPhys.Rev.E106014115 mixturesCommun.Phys.4202
[94] SammüllerF,HermannSandSchmidtM2023Comparative [116] BuzzaccaroS,TripodiA,RusconiR,VigoloDandPiazzaR
studyofforce-basedclassicaldensityfunctionaltheory 2008KineticsofsedimentationincolloidalsuspensionsJ.
Phys.Rev.E107034109 Phys.:Condens.Matter20494219
[95] HermannSandSchmidtM2022Forcebalanceinthermal [117] PiazzaR,BuzzaccaroS,SecchiEandParolaA2012What
quantummany-bodysystemsfromNoether’stheoremJ. buoyancyreallyis.AgeneralizedArchimedes’principle
Phys.A:Math.Theor.55464003 forsedimentationandultracentrifugationSoftMatter
[96] SammüllerF,HermannS,delasHerasDandSchmidtM 87112
2023Noether-constrainedcorrelationsinequilibrium [118] ArcherAJandEvansR2004Dynamicaldensityfunctional
liquidsPhys.Rev.Lett.130268203 theoryanditsapplicationtospinodaldecompositionJ.
[97] RobitschkoS,SammüllerF,SchmidtMandHermannS2023 Chem.Phys.1214246
HyperforcebalancefromthermalNoetherinvarianceof [119] teVrugtM,LöwenHandWittkowskiR2020Classical
anyobservable(arXiv:2308.12098) dynamicaldensityfunctionaltheory:fromfundamentals
[98] HermannS,SammüllerFandSchmidtM2024Noether toapplicationsAdv.Phys.69121
invariancetheoryfortheequilibriumforcestructureof [120] teVrugtMandWittkowskiR2023Perspective:New
softmatter(arXiv:2401.14971) directionsindynamicaldensityfunctionaltheoryJ.Phys.:
[99] BaydinAG,PearlmutterBA,RadulAAandSiskindJM Condens.Matter35041501
2018Automaticdifferentiationinmachinelearning:a [121] BaezJCandFongB2013ANoethertheoremforMarkov
surveyJ.Mach.Learn.Res.181 processesJ.Math.Phys.54013301
[100] CholletF2017DeepLearningWithPython(Manning [122] MarvianIandSpekkensRW2014ExtendingNoether’s
Publications) theorembyquantifyingtheasymmetryofquantumstates
[101] BraderJMandSchmidtM2014Dynamiccorrelationsin Nat.Commun.53821
Brownianmany-bodysystemsJ.Chem.Phys. [123] SasaSandYokokuraY2016Thermodynamicentropyasa
140034104 NoetherinvariantPhys.Rev.Lett.116140601
[102] BraderJMandSchmidtM2013Nonequilibrium [124] SasaS,SugiuraSandYokokuraY2019Thermodynamical
Ornstein-ZernikerelationforBrownianmany-body pathintegralandemergentsymmetryPhys.Rev.E
dynamicsJ.Chem.Phys.139104108 99022109
[103] GonzálezA,WhiteJA,RománFL,VelascoSandEvansR [125] RevzenM1970Functionalintegralsinstatisticalphysics
1997Densityfunctionaltheoryforsmallsystems:hard Am.J.Phys.38611
spheresinaclosedsphericalcavityPhys.Rev.Lett. [126] BudkovYAandKolesnikovAL2022Modified
792466 Poisson–Boltzmannequationsandmacroscopicforcesin
[104] WhiteJA,GonzálezA,RománFLandVelascoS2000 inhomogeneousionicfluidsJ.Stat.Mech.053205
Density-functionaltheoryofinhomogeneousfluidsinthe [127] BrandyshevPEandBudkovYA2023Noether’ssecond
canonicalensemblePhys.Rev.Lett.841220 theoremandcovariantfieldtheoryofmechanicalstresses
[105] DwandaruWSBandSchmidtM2011Variationalprinciple ininhomogeneousionicfluidsJ.Chem.Phys.158174114
ofclassicaldensityfunctionaltheoryviaLevy’s [128] BravettiA,Garcia-ArizaMAandTapiasD2023
constrainedsearchmethodPhys.Rev.E83061133 ThermodynamicentropyasaNoetherinvariantfrom
[106] delasHerasDandSchmidtM2014Fullcanonical contactgeometryEntropy251082
informationfromgrandpotentialdensityfunctionaltheory [129] LovettRA,MouCYandBuffFP1976Thestructureofthe
Phys.Rev.Lett.113238304 liquid-vaporinterfaceJ.Chem.Phys.65570
[107] FrenkelDandSmitB2023UnderstandingMolecular [130] WertheimMS1976Correlationsintheliquid-vapor
Simulation:FromAlgorithmstoApplications3rdedn interfaceJ.Chem.Phys.652377
(Academic) [131] ChanGK-LandFinkenR2005Time-dependentdensity
[108] WildingNB2001Computersimulationoffluidphase functionaltheoryofclassicalfluidsPhys.Rev.Lett.
transitionsAm.J.Phys.691147 94183001
22

J.Phys.:Condens.Matter36(2024)243002 TopicalReview
[132] GoddardBD,NoldA,SavvaN,PavliotisGAand [153] JungG,BiroliGandBerthierL2023Predictingdynamic
KalliadasisS2012Generaldynamicaldensityfunctional heterogeneityinglass-formingliquidsbyphysics-inspired
theoryforclassicalfluidsPhys.Rev.Lett.109120603 machinelearningPhys.Rev.Lett.130238202
[133] GoddardBD,Mills-WilliamsRD,OttobreMand [154] BinderK,BlockBJ,VirnauPandTrösterA2012Beyond
PavliotisG2021Well-posednessandequilibrium thevanderWaalsloop:whatcanbelearnedfrom
behaviourofoverdampeddynamicdensityfunctional simulatingLennard–Jonesfluidsinsidetheregionofphase
theory(arXiv:2002.11663) coexistenceAm.J.Phys.801099
[134] SchillingT2022Coarse-grainedmodellingoutof [155] LeithallGandSchmidtM2011Densityfunctionalforhard
equilibriumPhys.Rep.9721 hyperspheresfromatensorial-diagrammaticseriesPhys.
[135] delasHerasDandSchmidtM2018Velocitygradientpower Rev.E83021201
functionalforBrowniandynamicsPhys.Rev.Lett. [156] SchmidtM2011Staticsanddynamicsofinhomogeneous
120028001 liquidsviatheinternal-energyfunctionalPhys.Rev.E
[136] StuhlmüllerNCX,EckertT,delasHerasDandSchmidtM 84051203
2018Structuralnonequilibriumforcesindrivencolloidal [157] CohenTSandWellingM2016Groupequivariant
systemsPhys.Rev.Lett.121098002 convolutionalnetworksProc.33rdInt.Conf.onMachine
[137] delasHerasDandSchmidtM2020Flowandstructurein Learning(availableat:http://proceedings.mlr.press/v48/
nonequilibriumBrownianmany-bodysystemsPhys.Rev. cohenc16.pdf)
Lett.125018001 [158] WeilerM,GeigerM,WellingM,BoomsmaWandCohenT
[138] RoyallCP,DzubiellaJ,SchmidtMandvanBlaaderenA 20183DsteerableCNNs:learningrotationallyequivariant
2007Non-equilibriumsedimentationofcolloidsonthe featuresinvolumetricdataProc.32ndInt.Conf.on
particlescalePhys.Rev.Lett.98188304 NeuralInformationProcessingSystems(availableat:
[139] BierM,vanRoijR,DijkstraMandvanderSchootP2008 https://proceedings.neurips.cc/paper_files/paper/2018/file/
Self-diffusionofparticlesincomplexfluids:temporary 488e4104520c6aab692863cc1dba45af-Paper.pdf)
cagesandpermanentbarriersPhys.Rev.Lett.101215901 [159] FinziM,StantonS,IzmailovPandWilsonAG2020
[140] StopperD,ThorneyworkAL,DullensRPAandRothR Generalizingconvolutionalneuralnetworksfor
2018BulkdynamicsofBrownianharddisks:dynamical equivariancetoLiegroupsonarbitrarycontinuousdata
densityfunctionaltheoryversusexperimentson Proc.37thInt.Conf.onMachineLearning(availableat:
two-dimensionalcolloidalhardspheresJ.Chem.Phys. http://proceedings.mlr.press/v119/finzi20a/finzi20a.pdf)
148104501 [160] SatorrasVG,HoogeboomEandWellingM2021E(n)
[141] TreffenstädtLLandSchmidtM2021Universalityindriven equivariantgraphneuralnetworksProc.38thInt.Conf.on
andequilibriumhardsphereliquiddynamicsPhys.Rev. MachineLearning(Proc.MachineLearningResearchvol
Lett.126058002 139)edMMeilaandTZhang(PMLR)p9323
[142] TreffenstädtLL,SchindlerTandSchmidtM2022Dynamic [161] BatznerS,MusaelianA,SunL,GeigerM,MailoaJP,
decayandsuperadiabaticforcesinthevanHovedynamics KornbluthM,MolinariN,SmidtTEandKozinskyB2022
ofbulkhardspherefluidsSciPostPhys.12133 E(3)-equivariantgraphneuralnetworksfordata-efficient
[143] RennerJ,SchmidtManddelasHerasD2023 andaccurateinteratomicpotentialsNat.Commun.132453
Reduced-varianceorientationaldistributionfunctionsfrom [162] BatznerS,MusaelianAandKozinskyB2023Advancing
torquesamplingJ.Phys.:Condens.Matter35235901 molecularsimulationwithequivariantinteratomic
[144] TokatlyIV2005Quantummany-bodydynamicsina potentialsNat.Rev.Phys.5437
Lagrangianframe:I.Equationsofmotionand [163] MusaelianA,BatznerS,JohanssonA,SunL,OwenCJ,
conservationlawsPhys.Rev.B71165104 KornbluthMandKozinskyB2023Learninglocal
[145] TokatlyIV2005Quantummany-bodydynamicsina equivariantrepresentationsforlarge-scaleatomistic
Lagrangianframe:II.Geometricformulationof dynamicsNat.Commun.14579
time-dependentdensityfunctionaltheoryPhys.Rev.B [164] MolineroVandMooreEB2009Watermodeledasan
71165105 intermediateelementbetweencarbonandsiliconJ.Phys.
[146] TokatlyIV2007Time-dependentdeformationfunctional Chem.B1134008
theoryPhys.Rev.B75125105 [165] CoeMK,EvansRandWildingNB2022Thecoexistence
[147] TchenkoueM-LM,PenzM,TheophilouI,RuggenthalerM curveandsurfacetensionofamonatomicwatermodelJ.
andRubioA2019Forcebalanceapproachforadvanced Chem.Phys.156154505
approximationsindensityfunctionaltheoriesJ.Chem. [166] CoxSJ2020Dielectricresponsewithshort-ranged
Phys.151154107 electrostaticsProc.NatlAcad.Sci.11719746
[148] TarantinoWandUllrichCA2021Areformulationof [167] BuiATandCoxSJ2024Aclassicaldensityfunctional
time-dependentKohn-Shamtheoryintermsofthesecond theoryforsolvationacrosslengthscales
timederivativeofthedensityJ.Chem.Phys.154204112 (arXiv:2402.02873)
[149] SchmidtMandBraderJM2013Powerfunctionaltheoryfor [168] JungGetal2023Roadmaponmachinelearningglassy
BrowniandynamicsJ.Chem.Phys.138214101 liquids(arXiv:2311.14752)
[150] SchmidtM2015Quantumpowerfunctionaltheoryfor [169] SammüllerF,delasHerasDandSchmidtM2023
many-bodydynamicsJ.Chem.Phys.143174108 Inhomogeneoussteadysheardynamicsofathree-body
[151] SchmidtM2018PowerfunctionaltheoryforNewtonian colloidalgelformerJ.Chem.Phys.158054908
many-bodydynamicsJ.Chem.Phys.148044502 [170] HierarchicalStructureandMachineLearning(HISML)2023
[152] KarniadakisGE,KevrekidisIG,LuL,PerdikarisP,WangS Int.WorkshoponthePhysicsandChemistryof
andYangL2021Physics-informedmachinelearningNat. Many-BodySystems(InstituteforSolid-StatePhysics,The
Rev.Phys.3422 UniversityofTokyo,Japan,2–13October2023)
23