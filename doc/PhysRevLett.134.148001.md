|     |     |     |          | PHYSICAL |           | REVIEW |         | LETTERS       | 134, | 148001 |       | (2025) |     |     |     |
| --- | --- | --- | -------- | -------- | --------- | ------ | ------- | ------------- | ---- | ------ | ----- | ------ | --- | --- | --- |
|     |     |     | Learning |          | Classical |        | Density | Functionals   |      | for    | Ionic | Fluids |     |     |     |
|     |     |     |          |          | Anna      | T.     | Bui     | 1 and Stephen | J.   | Cox    | 2,*   |        |     |     |     |
1Yusuf
Hamied Department of Chemistry, University of Cambridge, Lensfield Road, Cambridge, CB2 1EW, United Kingdom
2Department
|     |     |     |           | of Chemistry, | Durham    |       | University, | South   | Road, | Durham,   | DH1 | 3LE,     | United Kingdom |     |     |
| --- | --- | --- | --------- | ------------- | --------- | ----- | ----------- | ------- | ----- | --------- | --- | -------- | -------------- | --- | --- |
|     |     |     | (Received |               | 4 October | 2024; | accepted    | 4 March | 2025; | published |     | 11 April | 2025)          |     |     |
Accurate and efficient theoretical techniques for describing ionic fluids are highly desirable for many
applicationsacrossthephysical,biological,and materials sciences. Witharigorousstatisticalmechanical
foundation, classical density functional theory (cDFT) is an appealing approach, but the competition
between strong Coulombic interactions and steric repulsion limits the accuracy of current approximate
functionals.Here,weextendarecentlypresentedmachinelearning(ML)approach[Sammülleretal.,Proc.
Natl.Acad.Sci.U.S.A.,120,e2312484120(2023)]designedforsystemswithshort-rangedinteractionsto
ionicfluids.Byadoptingideasfromlocalmolecularfieldtheory,theframeworkwepresentamountstousing
neural networks to learn the local relationship between the one-body direct correlation functions and
inhomogeneousdensityprofilesfora“mimic”short-rangedsystem,witheffectsoflong-rangedinteractions
accounted for in a mean-field, yet well-controlled, manner. By comparing to results from molecular
simulations, we show that our approach accurately describes the structure and thermodynamics of
prototypicalmodelsforelectrolytesolutionsandionicliquids,including size-asymmetricand multivalent
systems.TheframeworkwepresentactsasanimportantsteptowardextendingMLapproachesforcDFTto
|     | systems |     | with accurate | interatomic |     | potentials. |     |     |     |     |     |     |     |     |     |
| --- | ------- | --- | ------------- | ----------- | --- | ----------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
DOI: 10.1103/PhysRevLett.134.148001
The behavior of ionic fluids underlies a vast array of F ð e x Þ ½fρ
|                                                     |     |     |     |     |     |     |     | for   | the excess | intrinsic |     | free     | energy functional |            | νg(cid:2), |
| --------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | ----- | ---------- | --------- | --- | -------- | ----------------- | ---------- | ---------- |
| physicalandbiologicalphenomenaaswellastechnological |     |     |     |     |     |     |     |       |            |           |     |          |                   |            | i n t r    |
|                                                     |     |     |     |     |     |     |     | where | ρ          | denotes   | the | one-body | density           | of species | ν. For     |
ν
applications, ranging from electrolyte solutions controlling hard sphere fluids, functionals based on Rosenfeld’s fun-
protein folding [1] to room-temperature ionic liquids [18–21]
|     |     |     |     |     |     |     |     | damental |     | measure | theory |     | (FMT) | have | proven |
| --- | --- | --- | --- | --- | --- | --- | --- | -------- | --- | ------- | ------ | --- | ----- | ---- | ------ |
in energy storage devices [2]. A fundamental topic that highly successful. For simple liquids with square-well,
continues to attract enormous interest both experimentally Lennard–Jones
|           |               |     |        |        |           |     |         | Yukawa, |          | or  |     |             | interaction | potentials, | hard |
| --------- | ------------- | --- | ------ | ------ | --------- | --- | ------- | ------- | -------- | --- | --- | ----------- | ----------- | ----------- | ---- |
| [3–7] and | theoretically |     | [8–13] | is the | structure | and | thermo- |         |          |     |     |             |             |             |      |
|           |               |     |        |        |           |     |         | sphere  | mixtures |     | act | as suitable | reference   | systems,    | with |
dynamicsofionsnearchargedinterfaces,inparticular,how
effectsofattractiveinteractionsdescribedreasonablywellin
| the nature | of both | theelectrolyte |     | and | solid | surface | impacts |     |            |         |     |          |              |          |       |
| ---------- | ------- | -------------- | --- | --- | ----- | ------- | ------- | --- | ---------- | ------- | --- | -------- | ------------ | -------- | ----- |
|            |         |                |     |     |       |         |         | a   | mean-field | fashion |     | [22–24]. | In contrast, | existing | func- |
Poisson–
the properties of the electric double layer (EDL). tionals for ionic fluids are far less accurate, failing to
| Boltzmann | (PB) | theory | and | its linearized |     | Debye-Hückel |     |            |     |         |     |           |         |           |     |
| --------- | ---- | ------ | --- | -------------- | --- | ------------ | --- | ---------- | --- | ------- | --- | --------- | ------- | --------- | --- |
|           |      |        |     |                |     |              |     | adequately |     | capture | the | interplay | between | Coulombic | and |
form provide the basis for much of our understanding of steric interactions [25–28]. In this Letter, we present a
| ionic fluids. | Their |     | neglect | of correlations |     | arising | from |          |     |               |     |         |          |         |           |
| ------------- | ----- | --- | ------- | --------------- | --- | ------- | ---- | -------- | --- | ------------- | --- | ------- | -------- | ------- | --------- |
|               |       |     |         |                 |     |         |      | strategy |     | that utilizes |     | machine | learning | (ML) to | construct |
nonelectrostaticinteractions,however,restrictstheirvalidity accurate free energy functionals for ionic fluids.
| to fluids | of low    | ionic     | strength.  |            |           |        |              |              |           |         |       |           |                          |               |        |
| --------- | --------- | --------- | ---------- | ---------- | --------- | ------ | ------------ | ------------ | --------- | ------- | ----- | --------- | ------------------------ | ------------- | ------ |
|           |           |           |            |            |           |        |              |              | The rapid | advance |       | of modern | ML                       | approaches    | means  |
| Classical | density   |           | functional | theory     |           | (cDFT) | [14–17]      |              |           |         |       |           |                          |               |        |
|           |           |           |            |            |           |        |              | there        | has       | been    | much  | recent    | interest                 | in “learning” | repre- |
| provides  | a natural | framework |            | for        | including |        | correlations |              |           |         |       | e x       |                          |               |        |
|           |           |           |            |            |           |        |              | sentationsof |           | the     | exact | Fð        | Þ ½fρ νg(cid:2) [29–35]. | Herewe        | build  |
| omitted   | by PB     | theory,   | and        | has proven |           | to be  | a powerful   |              |           |         |       | in t r    |                          |               |        |
onthemethodproposedbySammülleretal.[36],inwhich
| approach                               | to describe |     | equilibrium |       | structure    | and            | thermody- |     |          |        |             |              |           |                         |     |
| -------------------------------------- | ----------- | --- | ----------- | ----- | ------------ | -------------- | --------- | --- | -------- | ------ | ----------- | ------------ | --------- | ----------------------- | --- |
|                                        |             |     |             |       |              |                |           | the | one-body | direct | correlation |              | functions |                         |     |
| namics                                 | of fluids   | in  | general.    | While | in principle |                | an exact  |     |          |        |             |              |           |                         |     |
| theory,historically,cDFTreliesonmaking |             |     |             |       |              | approximations |           |     |          |        |             |              |           |                         |     |
|                                        |             |     |             |       |              |                |           |     |          |        |             |              | βδF       | ð e x Þ ½ f ρ νg(cid:2) |     |
|                                        |             |     |             |       |              |                |           |     |          | cð 1Þ  | ðr;½fρ      | νg(cid:2)Þ¼− |           | i n t r                 |     |
|                                        |             |     |             |       |              |                |           |     |          | ν      |             |              |           |                         | ð1Þ |
δ ρ ð r Þ
ν
*Contact
author: stephen.j.cox@durham.ac.uk
|     |     |     |     |     |     |     |     | are | learned | by  | generating | inhomogeneous |     | density | profiles |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ------- | --- | ---------- | ------------- | --- | ------- | -------- |
Published by the American Physical Society under the terms of inthepresenceofvariousexternalandchemicalpotentials
| the Creative | Commons      |     | Attribution |      | 4.0 International |             | license. |     |       |           |     |      |              |               |     |
| ------------ | ------------ | --- | ----------- | ---- | ----------------- | ----------- | -------- | --- | ----- | --------- | --- | ---- | ------------ | ------------- | --- |
|              |              |     |             |      |                   |             |          | by  | grand | canonical |     | (GC) | simulations. | This approach | to  |
| Further      | distribution | of  | this work   | must | maintain          | attribution |          | to  |       |           |     |      |              |               |     |
article’s cDFT, dubbed “neural functional theory,” has been shown
| the author(s) | and | the | published |     | title, | journal | citation, |                                                  |     |     |     |     |     |     |     |
| ------------- | --- | --- | --------- | --- | ------ | ------- | --------- | ------------------------------------------------ | --- | --- | --- | --- | --- | --- | --- |
| and DOI.      |     |     |           |     |        |         |           | tooutperformFMT-basedapproachesforbothhardsphere |     |     |     |     |     |     |     |
0031-9007=25=134(14)=148001(8) 148001-1 Published by the American Physical Society

PHYSICAL REVIEW LETTERS 134, 148001 (2025)
fluidsandLennard-Jonesliquidsintermsofbothaccuracy [see Supplemental Material (SM) [49]]. We will also
and speed [36,37]. indicate quantities pertaining to the mimic system with a
Two key features underpin the success of the neural subscript “R” and focus on behaviors at a reduced
functionalapproach:(i)correlationsinthefluidareshort- temperature T(cid:3) ¼0.066, corresponding to supercritical
ranged(SR),suchthatthefunctionalrelationshipbetween conditions[67].Theone-bodydirectcorrelationfunctions
cð ν 1Þ and fρ νg is local; and (ii) the feasibility of GC of the mimic system can be exactly written as
simulationstoproduceinhomogeneousdensityprofilesof
sufficient quality to form a reliable training set. Ionic cð R 1 ; Þ ν ðrÞ¼lnΛ3 ν ρ R;νðrÞþβV R;νðrÞþβq ν ϕ R ðrÞ−βμ R;ν ; ð3Þ
fluids pose challenges on both fronts. First, the long-
ranged (LR) nature of the Coulomb potential leads to a where Λ ν, μ R;ν and q ν indicate the thermal de Broglie
nonlocal relationship between cð ν 1Þ and fρ νg. Second, GC wavelength, chemical potential, and point charge of
simulations for ionic systems raise delicate questions species ν, respectively, V R;ν encompasses any nonelec-
trostatic contributionstothe external potential forspecies
concerning electroneutrality, with various schemes pro-
ν, and, for now, ϕ is a general external electrostatic
posed that either insert individual ions or neutral pairs R
[38–42]. Even then, simulations corresponding exactly to potential;wewilllaterdiscusshowϕ R canbechosensuch
the GC ensemble where the number of each species can
that ρ R;νðrÞ¼ρ νðrÞ.
fluctuate are impractical, owing to poor acceptance rates To learn the functional relationship for cð
R
1
;
Þ
ν
ðr;½fρ R;νg(cid:2)Þ,
oftrialinsertionanddeletionmoves.Wecircumventboth we obtain data for the right hand side of Eq. (3) by
oftheseissuesbyadoptingconceptsfromlocalmolecular measuring ρ R;ν from simulations with known βV R;ν, βϕ R ,
field theory (LMFT) [43–47], which has been shown to and βμ R;ν. To this end, in line with Ref. [36], we perform
have close links to cDFT [48]. GC simulations in a planar geometry at different combi-
We initially focus our efforts on the prototypical model nations of fβV R;νg, βϕ
R
, and fβμ R;νg. Note that GC
of an ionic fluid: the restricted primitive model (RPM)
simulations are essential for the purpose of evaluating
comprising oppositely charged hard spheres of equal
Eq. (3) and, on their own, canonical methods such as
diameter σ, embedded in a uniform dielectric continuum.
molecular dynamics (MD) simulations are insufficient.
Later, we will also present results for a primitive model The form of v 0 means that each particle of the mimic
(i.e., size asymmetric) and a multivalent system. The
systemcanbeconsideredelectroneutral,comprisingbotha
scheme we propose can be briefly summarized. First, by
point charge and a compensating Gaussian charge distri-
employing neural networks, we find the one-body direct
bution[68].Assuch,inadditiontotranslationalmoves,we
correlationfunctionsforasuitablychosen“mimicsystem”
canreadilyperformGCparticleinsertions/deletions,along
whose electrostatic interactions are entirely short ranged. withsemi-GCswappingof“anions”and“cations”without
Then, by leveraging LMFT and its relation to cDFT, we
needing to worry about issues of electroneutrality [see
account for the net averaged effects of LR electrostatic
Fig. 1(a)]. We have found this highly beneficial for
interactions in a well-controlled fashion. When compared
converging our simulations, full details of which are
to molecular simulations, the framework we outline provided in SM [49]. In total, ∼2500 simulations have
describes inhomogeneous density profiles, the equation
been performed to gather training data.
ofstate,andthepropertiesoftheelectricdoublelayerinthe Foreachspecies,ν¼þor −,theneuralnetworkusedto
pre
c
s
D
en
F
s
T
e o
o
f
f
el
a
ect
s
r
h
ic
or
f
t
i
-
e
r
l
a
d
n
s
g
w
ed
ith
“
v
m
e
i
r
m
y
ic
h
”
igh
io
a
n
c
i
c
c
ur
f
a
l
c
u
y
id
.
—Our
representtherelationshipfρ R;νðzÞg→cð
R
1
;
Þ
ν
ðzÞisstructured
as follows. The input layer has two channels that are
overallstrategyfollowsthatofLMFT,inwhichweconsider
suppliedwiththediscretizedvaluesofthecationandanion
a suitably chosen mimic system whose interatomic inter-
density profiles in a window Δz¼3.6σ around the
actions are entirely short-ranged, and, when subject to a
suitably chosen one-body potential ϕ , has the same one- particular value of z. Following a fully connected multi-
R
layerperceptronofthreelayers,theoutputlayerconsistsof
bodydensitiesasthesystemofinterestwithLRinteractions
(the“full”system).ForsystemssuchastheRPM,whereLR a single node, which yields the predicted value of cð1Þ at
R;ν
interactions arise from the Coulomb potential, one adopts position z. For each ionic fluid considered, we train two
the exact splitting independent networks, one for the cation and one for the
anion.Toreducenoiseinthebulkstructurepredictions,we
1=r¼v 0ðrÞþv 1ðrÞ; ð2Þ alsoobtainedmodelsregularizedwithbulktwo-bodydirect
correlation functions as proposed in Ref. [69]. Details of
withv 0ðrÞ¼erfcðκrÞ=randv 1ðrÞ¼erfðκrÞ=r.Theinter-
ourtrainingprocedureareprovidedinSM[49],andalldata
atomic potential of the mimic system is then v 0, and the are openly available [70].
length scale κ−1 is chosen such that the mimic system We first assess the bulk structure predicted by the
accurately describes the SR correlations of the full functional. On the basis of the neural network, we make
system. In the following, we will work with κ−1 ¼1.8σ use of automatic differentiation and radial projection to
148001-2

|     |     |     |     |     | PHYSICAL |     | REVIEW LETTERS |     | 134, | 148001 (2025) |     |     |     |     |     |
| --- | --- | --- | --- | --- | -------- | --- | -------------- | --- | ---- | ------------- | --- | --- | --- | --- | --- |
(c)
| (a) |     |     |     |     |     | (b) |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
iv
i
FIG. 1. Structure of the SR mimic RPM. (a) Training data for the neural functional are obtained from GCMC simulations with
(i) insertion/deletion, (ii) position swapping, (iii) displacement, and (iv) mutation (identity exchange) moves. (b) The static structure
factorsfromcDFTagreewellwithresultsfrommolecularsimulationacrossthewholerangeofkfortheSRsystem,shownforabulk
systemwithσ3ρ ¼0.315.Inset:Atlowk,theSRsystemviolatestheperfectscreeningcondition,whereastheLRsystemobeysthe
R;(cid:4)
Stillinger–Lovettsumrule[seeEq.(5)].(c)Fortheappliedexternalpotentials(top),predictionsoftheiondensityprofiles(bottom)are
| in excellent |     | agreement | with | the | simulation | data. |     |     |     |     |     |     |     |     |     |
| ------------ | --- | --------- | ---- | --- | ---------- | ----- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
wherek−1istheDebyescreeninglength.Incontrast,forthe
| obtain | the | partial | two-body |     | direct | correlation | functions |     |     |     |     |     |     |     |     |
| ------ | --- | ------- | -------- | --- | ------ | ----------- | --------- | --- | --- | --- | --- | --- | --- | --- | --- |
D
cð 2 Þ ðrÞ(seeRef.[36]andSM[49]).Bysolvingthegeneral S ZZðkÞ>k2=k2 k→0,
|     |     |     |     |     |     |     |     | mimic | system | we  | observe |     |     | as  |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ----- | ------ | --- | ------- | --- | --- | --- | --- |
| ν λ |     |     |     |     |     |     |     |       |        |     |         |     |     | D   |     |
Ornstein-Zernike equation for mixtures [71,72], we then indicative of a lack of screening. Consistent with the
|        |     |       |             |     |           | hð2Þ |             | dielectric |     | response of | a short-ranged |     | water | model | [74], |
| ------ | --- | ----- | ----------- | --- | --------- | ---- | ----------- | ---------- | --- | ----------- | -------------- | --- | ----- | ----- | ----- |
| obtain | the | total | correlation |     | functions |      | ðrÞ and the |            |     |             |                |     |       |       |       |
νλ
S ðk t h es e d e v i a t io n s a p p e a r a t le n gt h s ca les f a r l a rger than the
| c o rre | s p o n | din g s t ru | c t u re | fa c t o rs | νλ  | Þ . W e | f u rt he r qu a n t if y |        |           |                  |               |         |        |       |     |
| ------- | ------- | ------------ | -------- | ----------- | --- | ------- | ------------------------- | ------ | --------- | ---------------- | ------------- | ------- | ------ | ----- | --- |
|         |         |              |          |             |     |         |                           | r an g | e s e p a | r a ti o n p r e | sc r ib e d b | y 2 π κ | 3. 5 σ | − 1 . |     |
t h e d e g r ee o f c o u p l in g b e t w ee n n u m b e r– n u m b er ( S ) , ¼
N N
number–charge(S NZ)andcharge–charge(S TurningtotheabilityofcDFTtopredictinhomogeneous
ZZ)densitiesby
|             |           |          |            |     |         |        |     | structure,     |     | the equilibrium | density |                   | profiles | of the  | mimic |
| ----------- | --------- | -------- | ---------- | --- | ------- | ------ | --- | -------------- | --- | --------------- | ------- | ----------------- | -------- | ------- | ----- |
| appropriate |           | weighted | summations |     |         |        |     |                |     |                 |         |                   |          |         |       |
|             |           |          |            |     |         |        |     | system         | can | be obtained     | by      | self-consistently |          | solving | the   |
|             | S NNðkÞ¼S |          | ðkÞþ2S     |     | þ−ðkÞþS | −−ðkÞ; |     | Euler-Lagrange |     | equation        |         |                   |          |         |       |
þþ
(cid:1)
|     | S   | NZðkÞ¼S | ðkÞ−S  |     | −−ðkÞ;  |        |     |     |     |              |            |           |              |         |     |
| --- | --- | ------- | ------ | --- | ------- | ------ | --- | --- | --- | ------------ | ---------- | --------- | ------------ | ------- | --- |
|     |     |         | þþ     |     |         |        |     |     | Λ3  | ρ R;νðrÞ¼exp | −βV        | R;νðrÞ−βq |              | ϕ RðrÞ  |     |
|     |     |         |        |     |         |        |     |     | ν   |              |            |           | ν            |         |     |
|     | S   | ZZðkÞ¼S | ðkÞ−2S |     | þ−ðkÞþS | −−ðkÞ: |     |     |     |              |            |           |              | (cid:3) |     |
|     |     |         |        |     |         |        | ð4Þ |     |     |              |            | 1         |              |         |     |
|     |     |         | þþ     |     |         |        |     |     |     |              | þβμ R;νþcð | Þ ðr;½fρ  | R;νg(cid:2)Þ | ;       | ð6Þ |
R ; ν
Figure1(b)showsthatthestaticstructurefactorsobtained
|     |     |     |     |     |     |     |     |     | cð 1 Þ |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ------ | --- | --- | --- | --- | --- | --- |
from the functional are in excellent agreement with results where ; ν is evaluated by the corresponding neural net-
R
fromamoleculardynamicssimulationofthemimicsystem work. As shown in Fig. 1(c) for a representative set of
|     |     |     |     |     |     |     |     |     |     |     |     | fρ  | R;νðzÞg |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ------- | --- | --- |
atthesamebulkdensities[73].ThesymmetryoftheRPMis external potentials, the resulting from cDFTare
well captured, reflected in S NZðkÞ¼0. Moreover, by inexcellentagreementwithreferencesimulationdataofthe
| comparing |     | to results | from | a   | MD simulation |     | of the full | mimic | system. |     |     |     |     |     |     |
| --------- | --- | ---------- | ---- | --- | ------------- | --- | ----------- | ----- | ------- | --- | --- | --- | --- | --- | --- |
system, we see that S NNðkÞ and S ZZðkÞ for the full and Accountingforlong-rangedelectrostaticswithLMFT—
| mimic | systems |     | agree | very well | at  | sufficiently | large k, |        |             |      |          |     |          |      |        |
| ----- | ------- | --- | ----- | --------- | --- | ------------ | -------- | ------ | ----------- | ---- | -------- | --- | -------- | ---- | ------ |
|       |         |     |       |           |     |              |          | Having | established | that | the cDFT |     | obtained | from | the ML |
κ−1
confirming that our choice of ¼1.8σ is sufficient for procedureisaccurateforaSRvariantoftheRPM,weturn
the mimic system to capture the SR correlations of the ourattentiontoincorporatingtheeffectsofLRelectrostatic
full system. Deviations of the SR system from the LR interactions. To do so, we will use concepts from LMFT.
system only manifest significantly in S ZZðkÞ at small k, in The premise of LMFT is that there exists a potential ϕ
R
| agreement |             | with | previous | works  | on     | the subject | [46,74].     | such | that |     |     |     |     |     |     |
| --------- | ----------- | ---- | -------- | ------ | ------ | ----------- | ------------ | ---- | ---- | --- | --- | --- | --- | --- | --- |
| In        | particular, | as   | shown    | in the | inset, | we see      | that S ZZðkÞ |      |      |     |     |     |     |     |     |
for the LR system strictly obeys the Stillinger-Lovett sum ρ νðr;½ϕ(cid:2);fμ νgÞ¼ρ R;νðr;½ϕ (cid:2);fμ R;νgÞ:
ð7Þ
R
rule [75,76]
|     |     |     |     |     |     |     |     | In  | Eq. (7), | we have | explicitly | indicated |     | the functional |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | -------- | ------- | ---------- | --------- | --- | -------------- | --- |
k2
|     |     |     |      |              |     |     |     | d e p | e n d e nc | e o f th e d | e n s itie s | o n t h | e e x te rn | a l e l e | c tr o st a ti c |
| --- | --- | --- | ---- | ------------ | --- | --- | --- | ----- | ---------- | ------------ | ------------ | ------- | ----------- | --------- | ---------------- |
|     |     |     | li m | D S ZZðkÞ¼1; |     |     | ð5Þ |       |            |              |              |         |             |           |                  |
|     |     |     | 0k   | 2            |     |     |     |       |            |              |              |         |             |           |                  |
k → p o te n t ia l [7 7 ]. A s s h o w n in R ef . [ 48 ] , w h e n r e c a s t i n a
148001-3

|     |     |     |     | PHYSICAL |     | REVIEW | LETTERS | 134, | 148001 | (2025) |     |     |     |     |     |
| --- | --- | --- | --- | -------- | --- | ------ | ------- | ---- | ------ | ------ | --- | --- | --- | --- | --- |
|     |     |     |     |          | (b) |        |         |      |        | (c)    |     |     |     |     |     |
(a)
T(cid:3) ¼0.066
FIG. 2. Structure and thermodynamics of the LR full system. cDFT for the RPM at with effects of LR electrostatic
interactions accounted by LMFT shows excellent agreement with reference molecular simulation data for (a) the equation of state,
(b)iondensityprofilesconfinedinaslit,and(c)withanappliedexternalpotential.In(a),weseethatourcDFTapproachoutperforms
the prediction obtained by combining the Carnahan-Starling equation of state for hard-sphere fluids (PCS) and the mean spherical
approximation(PMSA).FortheLRsystemin(c),theappliedexternalpotentialactsoveramuchlongerrangeandthechemicalpotentials
|             |       |          |     |              |        |     |           | ρ νðzÞ¼ρ |     | R;νðzÞ. |     |     |     |     |     |
| ----------- | ----- | -------- | --- | ------------ | ------ | --- | --------- | -------- | --- | ------- | --- | --- | --- | --- | --- |
| are shifted | lower | compared | to  | the SR mimic | system | in  | Fig. 1(c) | to yield |     |         |     |     |     |     |     |
cDFT framework, LMFT relates the one-body direct energy FðexÞ is accessible by functional line integration.
intr;R
correlationfunctionsofthefullandmimicsystemsthrough
Theresultofthisprocedure,showninFig.2(a),agreesvery
|              |               |            |                |     |      |        |     | w e l l w i | t h re f e | re n c e | s i m u l | a t io n | d a ta . | W e a l s o | se e t h a t , |
| ------------ | ------------- | ---------- | -------------- | --- | ---- | ------ | --- | ----------- | ---------- | -------- | --------- | -------- | -------- | ----------- | -------------- |
| cð 1Þ ðr;½fρ | νg(cid:2)Þ¼cð | 1 Þ ðr;½fρ | νg(cid:2)Þ−βΔμ |     | νþβq | ΔϕðrÞ; |     |             |            |          |           |          |          |             |                |
| ν            |               | ; ν        |                |     |      | ν      | ð8Þ |             |            |          |           |          |          |             |                |
R pa r t icu l a r ly a t h ig h e r d e n s i ti e s, E q . (1 2 ) p er f o r ms s ig n i fi -
|     |     |     |     |     |     |     |     | cantly better | than | the | analytical | approximation |     | that | results |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------- | ---- | --- | ---------- | ------------- | --- | ---- | ------- |
whichisanexactresult.AkeyinsightfromLMFT[43,44]
(PCS)
is that for an appropriate splitting of the potential [see from adding the Carnahan-Starling equation of state
|           | Δϕ  |                      |     |     |        |       |      | [79]andthemeansphericalapproximation(PMSA)[80,81], |     |     |     |     |     |     |     |
| --------- | --- | -------------------- | --- | --- | ------ | ----- | ---- | -------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
| Eq. (2)], |     | is well-approximated |     | by  | a mean | field | form |                                                    |     |     |     |     |     |     |     |
despitethefactthatPCSþPMSAformsthebasisforthevast
Z
1
|              |     |       |     |           |            |     |     | majority        | of current |     | state-of-the-art |     | functionals |     | for ionic |
| ------------ | --- | ----- | --- | --------- | ---------- | --- | --- | --------------- | ---------- | --- | ---------------- | --- | ----------- | --- | --------- |
| ΔϕðrÞ≡ϕðrÞ−ϕ |     | ðrÞ¼− |     | dr0nðr0Þv | 1ðjr−r0jÞ; |     | ð9Þ |                 |            |     |                  |     |             |     |           |
|              |     | R     |     | ϵ         |            |     |     |                 |            |     |                  |     |             |     |           |
|              |     |       |     |           |            |     |     | fluids [27,28]. |            |     |                  |     |             |     |           |
TheadvantagesofcDFTcombinedwithLMFTbecome
| where | ϵ isPthe | dielectric                           | constant | of  | the continuum |     | and |                                                   |     |     |     |     |     |     |     |
| ----- | -------- | ------------------------------------ | -------- | --- | ------------- | --- | --- | ------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
| n¼n   |          | q ρ                                  |          |     |               |     |     | evenclearerwheninhomogeneoussystemsareconsidered. |     |     |     |     |     |     |     |
|       | ¼        | ν νisthechargedensity.Forhomogeneous |          |     |               |     |     |                                                   |     |     |     |     |     |     |     |
R ν The equilibrium densities of the full system are given by
| systems, | Rodgers | and | Weeks | have also | derived | a   | thermo- |     |     |     |     |     |     |     |     |
| -------- | ------- | --- | ----- | --------- | ------- | --- | ------- | --- | --- | --- | --- | --- | --- | --- | --- |
(cid:1)
dynamic correction for the total energy, from which a Λ3 ρ νðrÞ¼exp −βV νðrÞ−βq ϕðrÞ
|            |     |              |         |       |     |     |     |     | ν   |     |     |     |     | ν       |     |
| ---------- | --- | ------------ | ------- | ----- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ------- | --- |
| correction | for | the pressure | follows | [78], |     |     |     |     |     |     |     |     |     | (cid:3) |     |
1Þ
|     |     |     |     |     |     |     |     |     |     |     | þβμ νþcð |     | ðr;½fρ | νg(cid:2)Þ ; | ð13Þ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | -------- | --- | ------ | ------------ | ---- |
ν
k T
|     |     | ΔP≡P−P |     | ¼−   | B :  |     | ð10Þ |                              |     |     |     |     |                     |     |     |
| --- | --- | ------ | --- | ---- | ---- | --- | ---- | ---------------------------- | --- | --- | --- | --- | ------------------- | --- | --- |
|     |     |        | R   | 2π3= | 2κ−3 |     |      |                              |     |     |     | 1Þ  |                     |     |     |
|     |     |        |     |      |      |     |      | wherethenonlocalfunctionalcð |     |     |     |     | isnowgivenbyEq.(8), |     |     |
ν
BasedonRef.[78],wehavefurtherderivedacorrectionfor togetherwithEqs.(9) and(11).FromacDFTperspective,
|              |     |           |      |           |     |     |     | we have | captured | all | strong | rapidly | varying | short-ranged |     |
| ------------ | --- | --------- | ---- | --------- | --- | --- | --- | ------- | -------- | --- | ------ | ------- | ------- | ------------ | --- |
| the chemical |     | potential | (see | SM [49]), |     |     |     |         |          |     |        |         |         |              |     |
cð1Þ,
|     |     |     |     |     |     |     |     | correlations | with | the | neural | networks |     | for while | the |
| --- | --- | --- | --- | --- | --- | --- | --- | ------------ | ---- | --- | ------ | -------- | --- | --------- | --- |
R;ν
q2
Δμ ≡μ −μ ¼− ν ffi ffiffi: effectsofLRelectrostaticinteractionsareincorporatedina
|     |     | ν   | ν   | R;ν κ−1 | p   |     | ð11Þ |              |     |                 |       |                 |     |         |        |
| --- | --- | --- | --- | ------- | --- | --- | ---- | ------------ | --- | --------------- | ----- | --------------- | --- | ------- | ------ |
|     |     |     |     |         | π   |     |      | mean-field   | yet | well-controlled |       | fashion.        |     |         |        |
|     |     |     |     |         |     |     |      | In practical |     | terms,          | for a | planargeometry, |     | Eq. (9) | can be |
WefirstconsiderthebulkthermodynamicsoftheRPM.
|              |     |          |         |           |      |               |      | recast as |     |     |                  |     |     |                 |      |
| ------------ | --- | -------- | ------- | --------- | ---- | ------------- | ---- | --------- | --- | --- | ---------------- | --- | --- | --------------- | ---- |
| The equation |     | of state | for the | LR system | is   | obtained      | with |           |     |     |                  |     |     |                 |      |
|              |     |          |         |           |      |               |      |           |     |     |                  |     |     | (cid:5) (cid:6) |      |
|              |     |          |         |           |      |               |      |           | 1   | X4π |                  |     |     | k2              |      |
|              | X   |          |         |           | e x  |               |      | ΔϕðzÞ¼−   |     |     | n˜ðkÞexpðikzÞexp |     |     | − ;             |      |
|              |     |          |         |           | Fð Þ | ½fρ νg(cid:2) |      |           |     |     |                  |     |     |                 | ð14Þ |
Pðfρ k Tρ νð1−cð 1 Þ ½fρ νg(cid:2)Þ− in t r ;R þΔP; ϵL k2 4κ2
| νgÞ¼ |     |     |     | ; ν |     |     |     |     |     | k≠0 |     |     |     |     |     |
| ---- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|      |     | B   | R   |     | V   |     |     |     |     |     |     |     |     |     |     |
ν
|     |     |     |     |     |     |     |     | wheren˜ | denotesaFouriercomponentofn,andListhetotal |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ------- | ------------------------------------------ | --- | --- | --- | --- | --- | --- |
ð12Þ
lengthoftheperiodiccell.InFig.2(b),weshowtheresults
where the sum of the first two terms is the negative of the fromourcDFTapproachfortheRPMconfinedbetweentwo
μ ¼μ
grandpotentialdensityofthemimicsystem.Theexcessfree repulsive walls for various values of −. The density
þ
148001-4

PHYSICAL REVIEW LETTERS 134, 148001 (2025)
profilesareinverygoodagreementwithreferencecanonical
MD simulation data in which the number of particles (a)
matches that obtained by integrating the density profiles
from cDFT. Our cDFT approach also works very well in
cases where the external potential contains an electrostatic
component,asillustratedinFig.2(c).Here,thefullsystemis
theLRcounterpartofthemimicsystemshowninFig.1(c),
emphasizing the premise of LMFT [see Eq. (7)].
The electric double layer and other ionic fluids—The (b)
results presented so far demonstrate that our cDFT
approach provides an efficient and accurate route to the
structure and thermodynamics of the RPM. As an appli-
cation, we turn our attention to the fundamental topic of
ongoing scientific interest: the electric double layer. We
also show that our approach is robust to the choice of
(c)
interatomic potential. Specifically, we also consider the
primitive model (PM) and a multivalent fluid.
As a simple model of an EDL-forming system, we
consider the RPM confined between two repulsive walls,
and in the presence of an electric field E z along the z
direction. The electrostatic potential that the LR system
feelsisϕðzÞ¼−E
z
z.Forthereferencesimulationdata,the
LR system was simulated at constant E z using the finite-
field approach [82–88]. As shown in Fig. 3(a), the ion FIG. 3. Accurately describing the EDL with cDFT for (a) the
distributions from our cDFT approach are in excellent RPM, (b) the PM, and (c) a multivalent fluid. In all cases,
agreement with the results from simulations. Notably, the confining walls are located at z=σ ¼(cid:4)7.2 in a periodic cell of
cDFT accurately describes the strong oscillations in the L=σ ¼18.1, and E z ¼1.7k B T=eσ. The resulting ion density
density profiles of co- and counterions. Moreover, as we profiles from cDFT are in excellent agreement with molecular
detail in SM [49], our functional is thermodynamically simulations, and obey the contact theorem [Eq. (15)].
consistent, satisfying the contact density theorem [89–91]
P¼−
X Z
dzρ νðzÞ
dV
d
ν
z
ðzÞ
−
2π
ϵ
σ2
s ; ð15Þ m
c
c
a
a
u
t
t
i
i
l
o
o
ti
n
n
v
s
a
t
l
o
o
e
f
n
σ
t
d
−
ia
s
¼
y
m
s
e
t
4
e
t
σ
e
m
r
=
,
3
σ,
w
a
b
n
e
u
d
t
c
σ
i
o
n
þ
n
c
s
r
¼
i
e
d
a
e
2
s
r
e
σ=
t
e
h
3
q
e
,
u
v
a
re
l
a
-
s
l
s
e
p
i
n
e
ze
c
cy
t
d
iv
o
e
a
f
l
n
y
t
i
.
h
o
e
F
ns
o
a
r
n
a
i
t
o
n
h
n
d
e
ν
such that q
−
=q
þ
¼2. We use the same temperature as for
w σ s h ¼ ichRr − 0 e L la d t z e n s ð t z h Þ e [ b 9 u 2 lk ] a p n re d ss io u n re d to en th si e ti s e u s rf a a t c c e o c n h t a a r c g t e w d i e th ns t i h ty e t o h b e se R rv P e M e , x T ce (cid:3) ll ¼ en ϵ t σ a k g B re T e = m jq e þ nt q b − e j t ¼ we 0 e . n 06 th 6 e . I n n eu b r o a t l h c c D as F e T s, a w nd e
walls.Obeyingthiscontacttheoremhasprovenachallenge simulations, both for inhomogeneous profiles and bulk
notonlyforintegralequationmethods[93–96],whichtend
equations of state, as further shown in SM [49]. Future
to violate key sum rules and are therefore generally work will pursue using neural functionals to understand
thermodynamically inconsistent [48,97], but also for most EDL capacitance [100] and surface force balance measure-
state-of-the-art cDFT functionals for ionic fluids [98,99]. ments [13], and to augment other cDFT approaches to
The accurate description of EDL structure and thermody- understand solvation [101]. The framework we have out-
namic consistency displayed by our LMFT-based neural lined should also find use in describing the dielectric
cDFTapproachconstitutesasignificantadvancementinthe response of polar fluids such as water [74,102,103].
theoretical description of ionic fluids.
The main advantage of the neural functional approach Acknowledgments—Via membership of the UK’s HEC
outlined in Ref. [36] is arguably that the local relationship
Materials Chemistry Consortium funded by EPSRC (EP/
between cð ν 1Þ and fρ νg permits application of the resulting X035859), this work used the ARCHER2 UK National
functional to system sizes far beyond those encountered Supercomputing Service. A.T.B. acknowledges funding
duringtrainingoftheML.ByusingtheframeworkofLMFT from the Oppenheimer Fund and Peterhouse College,
anditsrelationshiptocDFT,wehavesuccessfullyextended University of Cambridge. S.J.C. is a Royal Society
theneural functional approach toa casewherethe relation- University Research Fellow (Grant No. URF\R1\211144)
shipbetweencð ν 1Þ andfρ νgisnonlocal.Todemonstratethat at Durham University.
this methodology is not limited to the RPM, in Figs. 3(b)
and3(c),wepresentresultsforaPMandmultivalentsystem.
Dataavailability—Trainingdataandcodesupportingthe
For the PM, we have changed the sizes of the anion and findings of this study will be openly available [66,70].
148001-5

PHYSICAL REVIEW LETTERS 134, 148001 (2025)
[1] W.Kunz,J.Henle,andB.W.Ninham,‘ZurLehrevonder [19] R. Roth, R. Evans, A. Lang, and G. Kahl, Fundamental
Wirkung der Salze’ (about the science of the effect of measure theory for hard-sphere mixtures revisited: The
salts): Franz Hofmeister’s historical papers, Curr. Opin. White Bear version, J. Phys. Condens. Matter 14, 12063
Colloid Interface Sci. 9, 19 (2004). (2002).
[2] S. Kondrat, G. Feng, F. Bresme, M. Urbakh, and A.A. [20] H. Hansen-Goos and R. Roth, Density functional theory
Kornyshev, Theory and simulations of ionic liquids in forhard-spheremixtures:TheWhiteBearversionmarkII,
nanoconfinement, Chem. Rev. 123, 6668 (2023). J. Phys. Condens. Matter 18, 8413 (2006).
[3] R.M. Espinosa-Marzal, A. Arcifa, A. Rossi, and N.D. [21] R. Roth, Fundamental measure theory for hard-sphere
Spencer,Microslips to“avalanches”in confined,molecu- mixtures:Areview,J.Phys.Condens.Matter22,063102
lar layers of ionic liquids, J. Phys. Chem. Lett. 5, 179 (2010).
(2014). [22] E.KierlikandM.L.Rosinberg,Density-functionaltheory
[4] M.A. Gebbie, H.A. Dobbs, M. Valtiner, and J.N. forinhomogeneousfluids:Adsorptionofbinarymixtures,
Israelachvili, Long-range electrostatic screening in ionic Phys. Rev. A 44, 5025 (1991).
liquids, Proc. Natl. Acad. Sci. U.S.A. 112, 7432 (2015). [23] M.C. Stewart and R. Evans, Wetting and drying at a
[5] A.M. Smith, A.A. Lee, and S. Perkin, The electrostatic curved substrate: Long-ranged forces, Phys. Rev. E 71,
screening length in concentrated electrolytes increases 011602 (2005).
with concentration, J. Phys. Chem. Lett. 7, 2157 (2016). [24] A.J.Archer,B.Chacko,andR.Evans,Thestandardmean-
[6] A.A. Lee, C.S. Perez-Martinez, A.M. Smith, and S. fieldtreatmentofinter-particleattractioninclassicalDFT
Perkin,Underscreeninginconcentratedelectrolytes,Fara- is better than one might expect, J. Chem. Phys. 147,
day Discuss. 199, 239 (2017). 034501 (2017).
[7] M.A.Gebbie,A.M.Smith,H.A.Dobbs,A.A.Lee,G.G. [25] A. Härtel, M. Janssen, S. Samin, and R.v. Roij,
Warr, X. Banquy, M. Valtiner, M.W. Rutland, J.N. Fundamental measure theory for the electric double
Israelachvili,S.Perkin,andR.Atkin,Longrangeelectro- layer: Implications for blue-energy harvesting and
staticforcesinionicliquids,Chem.Commun.(Cambridge) water desalination, J. Phys. Condens. Matter 27, 194129
53, 1214 (2017). (2015).
[8] G.M. Torrie and J.P. Valleau, Electrical double layers. [26] A.Härtel,Structureofelectricdoublelayersincapacitive
I. Monte Carlo study of a uniformly charged surface, systems and to what extent (classical) density functional
J. Chem. Phys. 73, 5807 (1980). theory describes it, J. Phys. Condens. Matter 29, 423002
[9] C. Merlet, D.T. Limmer, M. Salanne, R. van Roij, P.A. (2017).
Madden, D. Chandler, and B. Rotenberg, The electric [27] R. Roth and D. Gillespie, Shells of charge: A density
double layer has a life ofits own, J. Phys. Chem. C 118, functional theory for charged hard spheres, J. Phys.
18291 (2014). Condens. Matter 28, 244006 (2016).
[10] M.Z.Bazant,B.D.Storey,andA.A.Kornyshev,Double [28] M. Bültmann and A. Härtel, The primitive model in
layer in ionic liquids: Overscreening versus crowding, classical density functional theory: Beyond the standard
Phys. Rev. Lett. 106, 046102 (2011). mean-field approximation, J. Phys. Condens. Matter 34,
[11] F.Coupette,A.A.Lee,andA.Härtel,Screeninglengthsin 235101 (2022).
ionic fluids, Phys. Rev. Lett. 121, 075501 (2018). [29] P. Cats, S. Kuipers, S. de Wind, R. van Damme, G.M.
[12] J.P. de Souza, Z.A.H. Goodwin, M. McEldrew, A.A. Coli,M.Dijkstra,andR.vanRoij,Machine-learningfree-
Kornyshev, and M.Z. Bazant, Interfacial layering in the energyfunctionalsusingdensityprofilesfromsimulations,
electricdoublelayerofionicliquids,Phys.Rev.Lett.125, APL Mater. 9, 031109 (2021).
116001 (2020). [30] J. Dijkman, M. Dijkstra, R. van Roij, M. Welling, J.-W.
[13] P. Cats, R. Evans, A. Härtel, and R. van Roij, Primitive vandeMeent,andB.Ensing,Learningneuralfree-energy
modelelectrolytesinthenearandfarfield:Decaylengths functionals with pair-correlation matching, Phys. Rev.
from DFTand simulations, J. Chem. Phys. 154, 124504 Lett. 134, 056103 (2025).
(2021). [31] A. Simon and M. Oettel, Machine learning appro-
[14] R. Evans, The nature of the liquid-vapour interface and aches to classical density functional theory, arXiv:2406
other topics in the statistical mechanics of non-uniform, .07345.
classical fluids, Adv. Phys. 28, 143 (1979). [32] S.-C. Lin, G. Martius, and M. Oettel, Analytical classical
[15] R.Evans,FundamentalsofInhomogeneousFluids,edited density functionals from an equation learning network,
by D. Henderson (Dekker, New York, 1992). J. Chem. Phys. 152, 021102 (2020).
[16] J.F. Lutsko, Recent Developments in Classical Density [33] L. Shang-Chun and M. Oettel, A classical density func-
FunctionalTheory,Adv.Chem.Phys.(JohnWiley&Sons, tional from machine learning and a convolutional neural
NewYork,2010)pp.1–92,10.1002/9780470564318.ch1. network, SciPost Phys. 6, 025 (2019).
[17] J. Hansen and I. McDonald, Theory of Simple Liquids: [34] A.Malpica-Morales,P.Yatsyshin,M.A.Durán-Olivencia,
With Applications to Soft Matter (Elsevier Science, New andS.Kalliadasis,Physics-informedBayesianinferenceof
York, 2013). external potentials in classical density-functional theory,
[18] Y. Rosenfeld, Free-energy model for the inhomogeneous J. Chem. Phys. 159, 104109 (2023).
hard-spherefluidmixtureanddensity-functionaltheoryof [35] R.Pederson,B.Kalita,andK.Burke,Machinelearningand
freezing, Phys. Rev. Lett. 63, 980 (1989). density functional theory, Nat. Rev. Phys. 4, 357 (2022).
148001-6

PHYSICAL REVIEW LETTERS 134, 148001 (2025)
[36] F. Sammüller, S. Hermann, D. de las Heras, and M. [51] A.P. Thompson, H.M. Aktulga, R. Berger, D.S.
Schmidt, Neural functional theory for inhomogeneous Bolintineanu, W.M. Brown, P.S. Crozier, P.J. in ’t Veld,
fluids: Fundamentals and applications, Proc. Natl. Acad. A.Kohlmeyer,S.G.Moore,T.D.Nguyen,R.Shan,M.J.
Sci. U.S.A. 120, e2312484120 (2023). Stevens, J. Tranchida, C. Trott, and S.J. Plimpton,
[37] F. Sammüller, M. Schmidt, and R. Evans, Neural density LAMMPS—a flexible simulation tool for particle-based
functional theory of liquid-gas phase coexistence, Phys. materials modeling at the atomic, meso, and continuum
Rev. X 15, 011013 (2025). scales, Comput. Phys. Commun. 271, 108171 (2022).
[38] J.C. Shelley and G.N. Patey, A configuration bias [52] T.SchneiderandE.Stoll,Molecular-dynamicsstudyofa
Monte Carlo method for ionic solutions, J. Chem. Phys. three-dimensional one-component model for distortive
100, 8265 (1994). phase transitions, Phys. Rev. B 17, 1302 (1978).
[39] Q. Yan and J.J. de Pablo, Hyper-parallel tempering [53] A. Härtel, S. Samin, and R. van Roij, Dense ionic fluids
Monte Carlo: Application to the Lennard-Jones fluid confined in planar capacitors: In- and out-of-plane struc-
and the restricted primitive model, J. Chem. Phys. 111, ture from classical density functional theory, J. Phys.
9509 (1999). Condens. Matter 28, 244007 (2016).
[40] F. Moučka, M. Lísal, J. Škvor, J. Jirsák, I. Nezbeda, and [54] J. Jover, A.J. Haslam, A. Galindo, G. Jackson, and E.A.
W.R.Smith, Molecularsimulation ofaqueouselectrolyte Müller,Pseudohard-spherepotentialforuseincontinuous
solubility.2.OsmoticensembleMonteCarlomethodology molecular-dynamics simulation of spherical and chain
forfreeenergyandsolubilitycalculationsandapplication molecules, J. Chem. Phys. 137, 144505 (2012).
to NaCl, J. Phys. Chem. B 115, 7849 (2011). [55] A.V. Brukhno, J. Grant, T.L. Underwood, K. Stratford,
[41] F. Moučka, D. Bratko, and A. Luzar, Electrolyte pore/ S.C. Parker, J.A. Purton, and N.B. Wilding,
solutionpartitioningbyexpandedgrandcanonicalensem- DL_MONTE: A multipurpose code for Monte Carlo
ble Monte Carlo simulation, J. Chem. Phys. 142, 124705 simulation, Mol. Simul. 47, 131 (2021).
(2015). [56] S.W. de Leeuw, J.W. Perram, E.R. Smith, and J.S.
[42] J. Kim, L. Belloni, and B. Rotenberg, Grand-canonical Rowlinson,Simulationofelectrostaticsystemsinperiodic
molecular dynamics simulations powered by a hybrid boundary conditions. I. Lattice sums and dielectric con-
4D nonequilibrium MD/MC method: Implementation stants, Proc. R. Soc. A 373, 27 (1997).
in LAMMPS and applications to electrolyte solutions, [57] R.HockneyandJ.Eastwood,ComputerSimulationUsing
J. Chem. Phys. 159, 144802 (2023). Particles (Adam-Hilger, New York, 1988).
[43] J.M. Rodgers and J.D. Weeks, Local molecular field [58] J. Kolafa and J.W. Perram, Cutoff errors in the Ewald
theoryforthetreatmentofelectrostatics,J.Phys.Condens. summationformulaeforpointchargesystems,Mol.Simul.
Matter 20, 494206 (2008). 9, 351 (1992).
[44] J.D. Weeks, K. Katsov, and K. Vollmayr, Roles of [59] F. Chollet, Deep Learning with Python (Manning Pub-
repulsiveandattractiveforcesindeterminingthestructure lications, New York, 2017), https://www.manning.com/
of nonuniform liquids: Generalized mean field theory, books/deep-learning-with-python.
Phys. Rev. Lett. 81, 4400 (1998). [60] T.Sayer,C.Zhang,andM.Sprik,Chargecompensationat
[45] J.M. Rodgers, C. Kaur, Y.-G. Chen, and J.D. Weeks, the interface between the polar NaClð111Þ surface and a
Attraction between like-charged walls: Short-ranged sim- NaClaqueoussolution,J.Chem.Phys.147,104702(2017).
ulationsusinglocalmolecularfieldtheory,Phys.Rev.Lett. [61] T. Sayer, M. Sprik, and C. Zhang, Finite electric dis-
97, 097801 (2006). placement simulations of polar ionic solid-electrolyte
[46] Y.-g.Chen,C.Kaur,andJ.D.Weeks,Connectingsystems interfaces: application to NaClð111Þ/aqueous NaCl sol-
with short and long ranged interactions: Local molecular ution, J. Chem. Phys. 150, 041716 (2019).
fieldtheoryforionicfluids,J.Phys.Chem.B108,19874 [62] F. Sedlmeier, D. Horinek, and R.R. Netz, Spatial corre-
(2004). lations of density and structural fluctuations in liquid
[47] R.C. Remsing, S. Liu, and J.D. Weeks, Long-ranged water: A comparative simulation study, J. Am. Chem.
contributions to solvation free energies from theory and Soc. 133, 1391 (2011).
short-ranged models, Proc. Natl. Acad. Sci. U.S.A. 113, [63] J.K. Johnson, J.A. Zollweg, and K.E. Gubbins, The
2819 (2016). Lennard-Jones equation of state revisited, Mol. Phys.
[48] A.J. Archer and R. Evans, Relationship between local 78, 591 (1993).
molecular field theory and density functional theory for [64] A.T. Bui, GCMC with Gaussian truncated potentials,
non-uniform liquids, J. Chem. Phys. 138, 014502 https://github.com/annatbui/GCMC (2024).
(2013). [65] S.J. Cox, Gaussian truncated potentials in LAMMPS,
[49] See Supplemental Material at http://link.aps.org/ https://github.com/uccasco/LMFT (2020).
supplemental/10.1103/PhysRevLett.134.148001, which [66] A.T. Bui and S.J. Cox, Learning cDFT for ionic fluids,
includes Refs. [50–66], for additional information on https://github.com/annatbui/ion-cdft (2024).
simulation details, training procedure, derivation of Δμ ν, [67] ThecriticaltemperatureoftheRPMisT(cid:3)
c
¼0.0492(from
and additional results. Ref. [39]).
[50] A.Z. Panagiotopoulos, *Molecular simulation of phase [68] D. Frenkel and B. Smit, Understanding Molecular
equilibria:Simple,ionicandpolymericfluids,FluidPhase Simulation: From Algorithms to Applications (Elsevier
Equilib. 76, 97 (1992). Science, New York, 2023).
148001-7

|     |     |     |     | PHYSICAL |     | REVIEW | LETTERS | 134, | 148001 | (2025) |     |     |     |     |     |
| --- | --- | --- | --- | -------- | --- | ------ | ------- | ---- | ------ | ------ | --- | --- | --- | --- | --- |
[69] F.SammüllerandM.Schmidt,Neuraldensityfunctionals: [87] T.SayerandS.J.Cox,Macroscopicsurfacechargesfrom
Locallearningandpair-correlationmatching,Phys.Rev.E microscopic simulations, J. Chem. Phys. 153, 164709
| 110, | L032601 | (2024). |     |     |     |     |     | (2020). |     |     |     |     |     |     |     |
| ---- | ------- | ------- | --- | --- | --- | --- | --- | ------- | --- | --- | --- | --- | --- | --- | --- |
A.T.BuiandS.J.Cox,Researchdatasupporting“Learn-
[70] [88] C. Zhang, T. Sayer, J. Hutter, and M. Sprik, Modelling
ing classical density functionals for ionic fluids”, Zenodo electrochemical systems with finite field molecular dy-
(2024), 10.5281/zenodo.15085645. namics, J. Phys. Energy 2, 032005 (2020).
|           |          |     |             |            |     |            |     | [89] D. | Henderson | and | L. Blum, | Some | exact | results | and the |
| --------- | -------- | --- | ----------- | ---------- | --- | ---------- | --- | ------- | --------- | --- | -------- | ---- | ----- | ------- | ------- |
| [71] L.S. | Ornstein | and | F. Zernike, | Accidental |     | deviations | of  |         |           |     |          |      |       |         |         |
density and opalescence at the critical point of a single application of the mean spherical approximation to
substance,Proc.R.Neth.Acad.ArtsSci.17,793(1914). charged hard spheres near a charged hard wall, J. Chem.
[72] R.J.Baxter,Ornstein–ZernikerelationandPercus–Yevick Phys. 69, 5441 (1978).
approximationforfluidmixtures,J.Chem.Phys.52,4559 [90] D. Henderson, L. Blum, and J.L. Lebowitz, An exact
|     |     |     |     |     |     |     |     | formula | for | the | contact | value of the | density | profile | of a |
| --- | --- | --- | --- | --- | --- | --- | --- | ------- | --- | --- | ------- | ------------ | ------- | ------- | ---- |
(2003).
[73] While GC simulations (i.e., known fμ νg) are required to system of charged hard spheres near a charged wall,
train the neural networks [see Eq. (3)], it is reasonable to J. Electroanal. Chem. 102, 315 (1979).
compare to average structures obtained with canonical [91] P.A.Martin,Sumrulesinchargedfluids,Rev.Mod.Phys.
|             |     |             |         |          |     |     |     | 60,                   | 1075 | (1988). |                                     |     |     |     |     |
| ----------- | --- | ----------- | ------- | -------- | --- | --- | --- | --------------------- | ---- | ------- | ----------------------------------- | --- | --- | --- | --- |
| simulations |     | at the same | average | density. |     |     |     |                       |      |         |                                     |     |     |     |     |
|             |     |             |         |          |     |     |     | [92] Thisequationforσ |      |         | assumesthattheelectrolyteiscentered |     |     |     |     |
[74] S.J. Cox, Dielectric response with short-ranged electro- s
|     |     |     |     |     |     |     |     |     |     |     |     |     |     | L   | z   |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
statics, Proc. Natl. Acad. Sci. U.S.A. 117, 19746 (2020). in a periodically replicated cell of length along the
| [75] F.H. | Stillinger | and | R. Lovett, | General | restriction |     | on the | direction.                                            |     |     |     |     |     |     |     |
| --------- | ---------- | --- | ---------- | ------- | ----------- | --- | ------ | ----------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
|           |            |     |            |         |             |     |        | [93] T.IchiyeandA.D.J.Haymet,Integralequationtheoryof |     |     |     |     |     |     |     |
distributionofionsinelectrolytes,J.Chem.Phys.49,1991
|     |     |     |     |     |     |     |     | ionic | solutions, |     | J. Chem. | Phys. 93, | 8954 (1990). |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | ----- | ---------- | --- | -------- | --------- | ------------ | --- | --- |
(1968).
|           |            |     |            |          |        |     |         | [94] K. | Nygård, | S.  | Sarman, | and R. Kjellander, |     | Local | order |
| --------- | ---------- | --- | ---------- | -------- | ------ | --- | ------- | ------- | ------- | --- | ------- | ------------------ | --- | ----- | ----- |
| [76] F.H. | Stillinger | and | R. Lovett, | Ion-pair | theory | of  | concen- |         |         |     |         |                    |     |       |       |
trated electrolytes. I. Basic concepts, J. Chem. Phys. 48, variations in confined hard-sphere fluids, J. Chem. Phys.
|                 |                   |           |              |                   |        |            |       | 139,                                               | 164701 | (2013).   |       |                  |         |               |     |
| --------------- | ----------------- | --------- | ------------ | ----------------- | ------ | ---------- | ----- | -------------------------------------------------- | ------ | --------- | ----- | ---------------- | ------- | ------------- | --- |
| 3858            | (1968).           |           |              |                   |        |            |       |                                                    |        |           |       |                  |         |               |     |
|                 |                   |           |              |                   |        |            |       | [95] Y.Jing,V.Jadhao,J.W.Zwanikken,andM.Olveradela |        |           |       |                  |         |               |     |
| [77] The number |                   | densities | also         | have a functional |        | dependence |       |                                                    |        |           |       |                  |         |               |     |
|                 |                   |           |              |                   |        |            |       | Cruz,                                              | Ionic  | structure | in    | liquids confined |         | by dielectric |     |
| on the          | non-electrostatic |           | contribution |                   | to the | external   | po-   |                                                    |        |           |       |                  |         |               |     |
|                 |                   |           |              |                   |        |            |       | interfaces,                                        |        | J. Chem.  | Phys. | 143, 194508      | (2015). |               |     |
| tential.        | As this           | is the    | same         | for both          | the    | full and   | mimic |                                                    |        |           |       |                  |         |               |     |
systems, i.e fV νg¼fV g, we do not indicate this [96] M . D in p a j oo h ,N .N . In t a n, T . T . D u ig n a n , E . B i a s in, J . L .
ν;R
|            |            |     |            |     |          |     |     | F u | lt on , S | . M . K ath | m an n | , G . K . S c he | n te r , a n | d C . J . | M u n d y, |
| ---------- | ---------- | --- | ---------- | --- | -------- | --- | --- | --- | --------- | ----------- | ------ | ---------------- | ------------ | --------- | ---------- |
| functional | dependence |     | explicitly | in  | Eq. (7). |     |     |     |           |             |        |                  |              |           |            |
BeyondtheDebye–Hückellimit:Towardageneraltheory
[78] J.M.RodgersandJ.D.Weeks,Accuratethermodynamics
forconcentratedelectrolytes,J.Chem.Phys.161,230901
| for short-ranged |     | truncations |     | of Coulomb |     | interactions | in  |     |     |     |     |     |     |     |     |
| ---------------- | --- | ----------- | --- | ---------- | --- | ------------ | --- | --- | --- | --- | --- | --- | --- | --- | --- |
(2024).
131,
| site-site | molecular | models, |     | J. Chem. | Phys. |     | 244108 |                                                       |     |     |     |     |     |     |     |
| --------- | --------- | ------- | --- | -------- | ----- | --- | ------ | ----------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- |
|           |           |         |     |          |       |     |        | [97] J.R.Henderson,FundamentalsofInhomogeneousFluids, |     |     |     |     |     |     |     |
(2009).
|                   |          |       |          |           |          |       |          | edited  | by                     | D. Henderson |                 | (Dekker, New     | York,      | 1992).    |          |
| ----------------- | -------- | ----- | -------- | --------- | -------- | ----- | -------- | ------- | ---------------------- | ------------ | --------------- | ---------------- | ---------- | --------- | -------- |
| [79] N.F.         | Carnahan | and   | K.E.     | Starling, | Equation |       | of state |         |                        |              |                 |                  |            |           |          |
|                   |          |       |          |           |          |       |          | [98] A. | Voukadinova,M.Valiskó, |              |                 | and D.Gillespie, |            | Assessing |          |
| for nonattracting |          | rigid | spheres, | J.        | Chem.    | Phys. | 51, 635  |         |                        |              |                 |                  |            |           |          |
|                   |          |       |          |           |          |       |          | the     | accuracy               | of           | three classical | density          | functional |           | theories |
(1969).
|     |     |     |     |     |     |     |     | of  | the electrical |     | double | layer, Phys. | Rev. | E 98, | 012116 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | -------------- | --- | ------ | ------------ | ---- | ----- | ------ |
[80] J.L.LebowitzandJ.K.Percus,Meansphericalmodelfor
(2018).
| lattice | gases | with extended |     | hard    | cores | and continuum |     |         |            |           |     |                 |      |     |         |
| ------- | ----- | ------------- | --- | ------- | ----- | ------------- | --- | ------- | ---------- | --------- | --- | --------------- | ---- | --- | ------- |
|         |       |               |     |         |       |               |     | [99] D. | Gillespie, | Restoring |     | the consistency | with | the | contact |
| fluids, | Phys. | Rev. 144,     | 251 | (1966). |       |               |     |         |            |           |     |                 |      |     |         |
densitytheoremofaclassicaldensityfunctionaltheoryof
| [81] L. Blum,    | Mean          | spherical | model       | for      | asymmetric  |                | electro- |             |          |        |              |                  |             |       |         |
| ---------------- | ------------- | --------- | ----------- | -------- | ----------- | -------------- | -------- | ----------- | -------- | ------ | ------------ | ---------------- | ----------- | ----- | ------- |
|                  |               |           |             |          |             |                |          | ions        | at a     | planar | electrical   | double layer,    | Phys.       | Rev.  | E 90,   |
| lytes,           | Mol. Phys.    | 30,       | 1529        | (1975).  |             |                |          | 052134      | (2014).  |        |              |                  |             |       |         |
| [82] M. Stengel, |               | N.A.      | Spaldin,    | and D.   | Vanderbilt, |                | Electric |             |          |        |              |                  |             |       |         |
|                  |               |           |             |          |             |                |          | [100] P.    | Cats and | R. van | Roij,        | The differential | capacitance |       | as a    |
| displacement     |               | as the    | fundamental | variable |             | in electronic- |          |             |          |        |              |                  |             |       |         |
|                  |               |           |             |          |             |                |          | probe       | for      | the    | electric     | double layer     | structure   |       | and the |
| structure        | calculations, |           | Nat.        | Phys. 5, | 304 (2009). |                |          |             |          |        |              |                  |             |       |         |
|                  |               |           |             |          |             |                |          | electrolyte |          | bulk   | composition, | J.               | Chem.       | Phys. | 155,    |
[83] C.ZhangandM.Sprik,Computingthedielectricconstant 104702 (2021).
of liquid water at constant dielectric displacement, Phys. [101] A.T. Bui and S.J. Cox, A classical density functional
| Rev.          | B 93, 144201 |     | (2016).    |                       |         |     |         |                                                     |        |           |        |                |     |       |       |
| ------------- | ------------ | --- | ---------- | --------------------- | ------- | --- | ------- | --------------------------------------------------- | ------ | --------- | ------ | -------------- | --- | ----- | ----- |
|               |              |     |            |                       |         |     |         | theory                                              | for    | solvation | across | length scales, | J.  | Chem. | Phys. |
| [84] C. Zhang | and          | M.  | Sprik,     | Finite field          | methods |     | for the |                                                     |        |           |        |                |     |       |       |
|               |              |     |            |                       |         |     |         | 161,                                                | 104103 | (2024).   |        |                |     |       |       |
| supercell     | modeling     |     | of charged | insulator/electrolyte |         |     | inter-  |                                                     |        |           |        |                |     |       |       |
|               |              |     |            |                       |         |     |         | [102] A.Gao,R.C.Remsing,andJ.D.Weeks,Localmolecular |        |           |        |                |     |       |       |
faces, Phys. Rev. B 94, 245309 (2016). fieldtheoryforCoulombinteractionsinaqueoussolutions,
[85] M. Sprik, Finite Maxwell field and electric displacement J. Phys. Chem. B 127, 809 (2023).
| Hamiltonians |            | derived | from | a current | dependent |     | Lagran- |            |         |     |      |                  |     |       |        |
| ------------ | ---------- | ------- | ---- | --------- | --------- | --- | ------- | ---------- | ------- | --- | ---- | ---------------- | --- | ----- | ------ |
|              |            |         |      |           |           |     |         | [103] J.M. | Rodgers | and | J.D. | Weeks, Interplay | of  | local | hydro- |
| gian,        | Mol. Phys. | 116,    | 3114 | (2018).   |           |     |         |            |         |     |      |                  |     |       |        |
gen-bondingandlong-rangeddipolarforcesinsimulations
[86] S.J. Cox and M. Sprik, Finite field formalism for bulk of confined water, Proc. Natl. Acad. Sci. U.S.A. 105,
| electrolytesolutions,J.Chem.Phys.151,064506(2019). |     |     |     |     |     |     |     | 19136 | (2008). |     |     |     |     |     |     |
| -------------------------------------------------- | --- | --- | --- | --- | --- | --- | --- | ----- | ------- | --- | --- | --- | --- | --- | --- |
148001-8