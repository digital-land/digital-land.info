DATASET_STR = """
address
agricultural-land-classification
air-quality-management-area
ancient-woodland
ancient-woodland-status
archaeological-priority-area
area-of-outstanding-natural-beauty
article-4-direction
article-4-direction-area
article-4-direction-rule
asset-of-community-value
attribution
battlefield
best-and-most-versatile-agricultural-land
biodiversity-net-gain-assessment
border
brownfield-land
brownfield-site
buffer-zone
building-preservation-notice
built-up-area
category
central-activities-zone
certificate-of-immunity
coastal-change-management-area
column
common-land-and-village-green
community-infrastructure-levy-schedule
company
conservation-area
conservation-area-document
conservation-area-document-type
contaminated-land
contribution-funding-status
contribution-purpose
control-of-major-accident-hazards-site
default
default-value
design-code
design-code-area
design-code-area-type
design-code-characteristic
design-code-rule
design-code-rule-category
design-code-status
developer-agreement
developer-agreement-contribution
developer-agreement-transaction
developer-agreement-type
development-corporation
development-metric
development-plan
development-plan-boundary
development-plan-boundary-type
development-plan-document
development-plan-document-type
development-plan-event
development-plan-geography
development-plan-geography-type
development-plan-status
development-plan-timetable
development-plan-type
development-policy
development-policy-area
development-policy-category
development-policy-metric
document
document-type
educational-establishment
employment-allocation
entity
entity-organisation
expect
expectation
fact
fact-resource
flood-risk-level
flood-risk-type
flood-risk-zone
flood-storage-area
forest-inventory
government-organisation
green-belt
green-belt-core
guardianship-site-and-english-heritage-site
gypsy-and-traveller-site
heritage-action-zone
heritage-at-risk
heritage-coast
historic-non-designed-rural-landscape-local-landscape-area
historic-stone-quarry
housing-allocation
hs2-safeguarded-area
infrastructure-funding-statement
infrastructure-project
infrastructure-project-decision
infrastructure-project-document
infrastructure-project-document-type
infrastructure-project-event
infrastructure-project-log
infrastructure-project-type
internal-drainage-board
internal-drainage-district
licence
listed-building
listed-building-grade
listed-building-outline
local-area-requirements
local-authority
local-authority-district
local-authority-type
local-enterprise-partnership
local-green-space
locally-listed-building
local-nature-recovery-strategy
local-nature-reserve
local-plan
local-plan-boundary
local-plan-document
local-plan-document-type
local-plan-event
local-planning-authority
local-plan-timetable
local-resilience-forum
local-resilience-forum-boundary
london-square
long-established-woodland
long-protected-woodland
main-river
metropolitan-open-land
mineral-safeguarding-area
national-nature-reserve
national-park
national-park-authority
nature-improvement-area
neighbourhood-forum
non-designated-and-locally-listed-historic-asset
non-designated-archeology-asset-of-national-importance
nonprofit
nuclear-safety-zone
old-entity
old-resource
open-space
ownership-status
parish
park-and-garden
park-and-garden-grade
passenger-transport-executive
permitted-development-right
permitted-development-right-part
phase
planning-application
planning-application-category
planning-application-condition
planning-application-document
planning-application-log
planning-application-status
planning-application-type
planning-condition
planning-condition-purpose
planning-condition-target
planning-condition-type
planning-decision
planning-decision-type
planning-development-category
planning-permission-status
planning-permission-type
policy
prefix
proposed-ramsar-site
protected-land
protected-view
protected-wreck-site
public-authority
public-safety-zone-around-airport
ramsar
realm
region
regional-park-authority
safeguarded-aerodrome
safeguarded-military-explosives-site
safeguarded-wharf
safety-hazard-area
scheduled-monument
self-and-custom-buildarea
site-category
site-of-special-scientific-interest
special-area-of-conservation
special-protection-area
street
suitable-alternative-green-space
title-boundary
transport-access-node
transport-under-tcpa-route
tree
tree-preservation-order
tree-preservation-zone
tree-preservation-zone-type
uprn
ward
waste-authority
wildbelt
wildlife
world-heritage-site
world-heritage-site-buffer-zone
""".strip()

LOCATION_STR = """
statistical-geography:E07000223
statistical-geography:E07000026
statistical-geography:E07000032
statistical-geography:E07000224
statistical-geography:E07000105
statistical-geography:E07000170
statistical-geography:E07000004
statistical-geography:E07000200
statistical-geography:E07000171
statistical-geography:E07000066
statistical-geography:E07000084
statistical-geography:E07000027
statistical-geography:E06000022
statistical-geography:E06000008
statistical-geography:E06000055
statistical-geography:E09000002
statistical-geography:E09000005
statistical-geography:E09000004
statistical-geography:E08000025
statistical-geography:E10000002
statistical-geography:E07000129
statistical-geography:E06000028
statistical-geography:E09000003
statistical-geography:E06000043
statistical-geography:E08000016
statistical-geography:E08000001
statistical-geography:E07000033
statistical-geography:E07000136
statistical-geography:E06000058
statistical-geography:E06000009
statistical-geography:E07000067
statistical-geography:E06000036
statistical-geography:E08000032
statistical-geography:E07000143
statistical-geography:E07000234
statistical-geography:E07000144
statistical-geography:E07000172
statistical-geography:E07000068
statistical-geography:E07000095
statistical-geography:E09000006
statistical-geography:E06000023
statistical-geography:E06000060
statistical-geography:E07000117
statistical-geography:E08000002
statistical-geography:E07000008
statistical-geography:E10000003
statistical-geography:E07000192
statistical-geography:E07000028
statistical-geography:E07000069
statistical-geography:E07000106
statistical-geography:E06000056
statistical-geography:E07000130
statistical-geography:E07000048
statistical-geography:E06000049
statistical-geography:E07000225
statistical-geography:E07000070
statistical-geography:E07000005
statistical-geography:E07000118
statistical-geography:E07000177
statistical-geography:E07000034
statistical-geography:E07000078
statistical-geography:E06000050
statistical-geography:E08000033
statistical-geography:E10000006
statistical-geography:E09000007
statistical-geography:E07000071
statistical-geography:E06000052
statistical-geography:E07000029
statistical-geography:E07000150
statistical-geography:E07000079
statistical-geography:E08000026
statistical-geography:E47000008
statistical-geography:E07000163
statistical-geography:E07000226
statistical-geography:E09000008
statistical-geography:E06000063
statistical-geography:E07000096
statistical-geography:E06000005
statistical-geography:E07000107
statistical-geography:E07000151
statistical-geography:E10000007
statistical-geography:E07000035
statistical-geography:E06000015
statistical-geography:E10000008
statistical-geography:E08000017
statistical-geography:E10000009
statistical-geography:E07000108
statistical-geography:E06000059
statistical-geography:E08000027
statistical-geography:E06000047
statistical-geography:E09000009
statistical-geography:E07000061
statistical-geography:E07000086
statistical-geography:E07000009
statistical-geography:E07000040
statistical-geography:E07000030
statistical-geography:E07000049
statistical-geography:E07000085
statistical-geography:E07000242
statistical-geography:E07000137
statistical-geography:E07000207
statistical-geography:E47000013
statistical-geography:E09000010
statistical-geography:E07000152
statistical-geography:E07000072
statistical-geography:E07000208
statistical-geography:E07000036
statistical-geography:E06000011
statistical-geography:E07000244
statistical-geography:E10000012
statistical-geography:E07000193
statistical-geography:E10000011
statistical-geography:E07000041
statistical-geography:E07000087
statistical-geography:E07000010
statistical-geography:E07000080
statistical-geography:E07000201
statistical-geography:E07000119
statistical-geography:E08000037
statistical-geography:E07000173
statistical-geography:E12000007
statistical-geography:E07000081
statistical-geography:E10000013
statistical-geography:E47000001
statistical-geography:E07000088
statistical-geography:E07000109
statistical-geography:E09000011
statistical-geography:E07000209
statistical-geography:E07000145
statistical-geography:E07000090
statistical-geography:E07000164
statistical-geography:E07000165
statistical-geography:E06000006
statistical-geography:E10000014
statistical-geography:E07000131
statistical-geography:E07000073
statistical-geography:E07000062
statistical-geography:E07000089
statistical-geography:E09000016
statistical-geography:E09000012
statistical-geography:E06000019
statistical-geography:E07000098
statistical-geography:E07000037
statistical-geography:E09000017
statistical-geography:E07000132
statistical-geography:E09000013
statistical-geography:E09000018
statistical-geography:E07000227
statistical-geography:E06000001
statistical-geography:E10000015
statistical-geography:E09000015
statistical-geography:E09000014
statistical-geography:E07000011
statistical-geography:E07000120
statistical-geography:E06000053
statistical-geography:E06000046
statistical-geography:E07000202
statistical-geography:E09000019
statistical-geography:E09000020
statistical-geography:E10000016
statistical-geography:E07000153
statistical-geography:E06000010
statistical-geography:E07000146
statistical-geography:E08000034
statistical-geography:E09000021
statistical-geography:E08000011
statistical-geography:E07000121
statistical-geography:E10000017
statistical-geography:E09000022
statistical-geography:E06000016
statistical-geography:E47000004
statistical-geography:E08000035
statistical-geography:E10000018
statistical-geography:E07000063
statistical-geography:E09000023
statistical-geography:E07000138
statistical-geography:E07000194
statistical-geography:E10000019
statistical-geography:E08000012
statistical-geography:E09000001
statistical-geography:E06000032
statistical-geography:E07000110
statistical-geography:E07000074
statistical-geography:E08000003
statistical-geography:E07000174
statistical-geography:E07000235
statistical-geography:E06000002
statistical-geography:E07000042
statistical-geography:E06000035
statistical-geography:E07000133
statistical-geography:E07000187
statistical-geography:E06000042
statistical-geography:E07000210
statistical-geography:E09000024
statistical-geography:E07000228
statistical-geography:E07000203
statistical-geography:E06000057
statistical-geography:E07000043
statistical-geography:E07000050
statistical-geography:E07000175
statistical-geography:E07000195
statistical-geography:E47000010
statistical-geography:E07000038
statistical-geography:E06000012
statistical-geography:E08000021
statistical-geography:E07000091
statistical-geography:E10000020
statistical-geography:E06000018
statistical-geography:E07000099
statistical-geography:E07000139
statistical-geography:E06000013
statistical-geography:E47000014
statistical-geography:E07000147
statistical-geography:E06000061
statistical-geography:E07000154
statistical-geography:E07000148
statistical-geography:E06000024
statistical-geography:E47000011
statistical-geography:E10000021
statistical-geography:E10000024
statistical-geography:E08000022
statistical-geography:E07000219
statistical-geography:E07000218
statistical-geography:E07000134
statistical-geography:E09000025
statistical-geography:E10000023
statistical-geography:E06000065
statistical-geography:E07000135
statistical-geography:E08000004
statistical-geography:E10000025
statistical-geography:E07000178
statistical-geography:E07000122
statistical-geography:E06000026
statistical-geography:E06000029
statistical-geography:E06000044
statistical-geography:E07000123
statistical-geography:E06000031
statistical-geography:E07000051
statistical-geography:E06000003
statistical-geography:E08000005
statistical-geography:E09000026
statistical-geography:E06000038
statistical-geography:E07000236
statistical-geography:E07000211
statistical-geography:E07000124
statistical-geography:E09000027
statistical-geography:E07000166
statistical-geography:E07000075
statistical-geography:E07000064
statistical-geography:E07000125
statistical-geography:E08000018
statistical-geography:E07000220
statistical-geography:E07000092
statistical-geography:E07000212
statistical-geography:E07000176
statistical-geography:E06000017
statistical-geography:E07000167
statistical-geography:E07000240
statistical-geography:E08000028
statistical-geography:E07000006
statistical-geography:E07000012
statistical-geography:E07000168
statistical-geography:E07000039
statistical-geography:E07000204
statistical-geography:E07000188
statistical-geography:E07000169
statistical-geography:E07000111
statistical-geography:E10000029
statistical-geography:E08000014
statistical-geography:E06000025
statistical-geography:E07000044
statistical-geography:E07000112
statistical-geography:E08000019
statistical-geography:E08000013
statistical-geography:E07000140
statistical-geography:E06000051
statistical-geography:E07000141
statistical-geography:E08000007
statistical-geography:E07000031
statistical-geography:E08000006
statistical-geography:E06000039
statistical-geography:E08000024
statistical-geography:E07000149
statistical-geography:E07000155
statistical-geography:E08000029
statistical-geography:E10000027
statistical-geography:E06000033
statistical-geography:E07000179
statistical-geography:E07000213
statistical-geography:E07000126
statistical-geography:E10000030
statistical-geography:E07000189
statistical-geography:E07000196
statistical-geography:E07000197
statistical-geography:E06000021
statistical-geography:E07000198
statistical-geography:E06000045
statistical-geography:E09000029
statistical-geography:E07000082
statistical-geography:E07000221
statistical-geography:E10000028
statistical-geography:E06000004
statistical-geography:E07000243
statistical-geography:E08000023
statistical-geography:E06000066
statistical-geography:E07000205
statistical-geography:E07000214
statistical-geography:E06000030
statistical-geography:E09000028
statistical-geography:E07000113
statistical-geography:E07000246
statistical-geography:E47000002
statistical-geography:E08000008
statistical-geography:E07000215
statistical-geography:E07000190
statistical-geography:E07000199
statistical-geography:E07000045
statistical-geography:E07000076
statistical-geography:E07000093
statistical-geography:E07000083
statistical-geography:E06000020
statistical-geography:E07000114
statistical-geography:E07000102
statistical-geography:E06000034
statistical-geography:E06000027
statistical-geography:E07000115
statistical-geography:E07000046
statistical-geography:E08000009
statistical-geography:E07000116
statistical-geography:E47000006
statistical-geography:E09000030
statistical-geography:E07000077
statistical-geography:E07000180
statistical-geography:E07000216
statistical-geography:E10000031
statistical-geography:E07000103
statistical-geography:E07000206
statistical-geography:E07000222
statistical-geography:E06000037
statistical-geography:E07000047
statistical-geography:E07000052
statistical-geography:E07000065
statistical-geography:E47000009
statistical-geography:E07000156
statistical-geography:E07000241
statistical-geography:E07000053
statistical-geography:E09000031
statistical-geography:E06000064
statistical-geography:E08000010
statistical-geography:E06000054
statistical-geography:E07000094
statistical-geography:E08000036
statistical-geography:E07000127
statistical-geography:E07000142
statistical-geography:E08000030
statistical-geography:E08000031
statistical-geography:E47000007
statistical-geography:E09000032
statistical-geography:E06000040
statistical-geography:E06000062
statistical-geography:E07000237
statistical-geography:E07000217
statistical-geography:E06000041
statistical-geography:E10000034
statistical-geography:E07000229
statistical-geography:E07000181
statistical-geography:E08000015
statistical-geography:E06000007
statistical-geography:E07000245
statistical-geography:E09000033
statistical-geography:E07000191
statistical-geography:E10000032
statistical-geography:E07000238
statistical-geography:E47000003
statistical-geography:E07000239
statistical-geography:E07000007
statistical-geography:E07000128
statistical-geography:E47000012
statistical-geography:E06000014
""".strip()

ORGANISATION_STR = """
1
2
3
4
5
6
7
8
9
600001
600001
600001
600001
600001
600001
600001
600001
600001
600001
600001
600001
600001
600001
600001
600001
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
66
67
68
69
70
71
72
73
74
75
76
77
78
79
80
81
82
83
84
85
86
87
88
89
90
91
92
93
94
95
96
97
98
99
100
101
102
103
104
105
106
107
108
109
110
111
112
113
114
115
116
117
118
119
120
121
122
123
124
125
126
127
128
129
130
131
132
133
134
135
136
137
138
139
140
141
142
143
144
145
146
147
148
149
150
151
152
153
154
155
156
157
158
159
160
161
162
163
164
165
166
167
168
169
170
171
172
173
174
175
176
177
178
179
180
181
182
183
184
185
186
187
188
189
190
191
192
193
194
195
196
197
198
199
200
201
202
203
204
205
206
207
208
209
210
211
212
213
214
215
216
217
218
219
220
221
222
223
224
225
226
227
228
229
230
231
232
233
234
235
236
237
238
239
240
241
242
243
244
245
246
247
248
249
250
251
252
253
254
255
256
257
258
259
260
261
262
263
264
265
266
267
268
269
270
271
272
273
274
275
276
277
278
279
280
281
282
283
284
285
286
287
288
289
290
291
292
293
294
295
296
297
298
299
300
301
302
303
304
305
306
307
308
309
310
311
312
313
314
315
316
317
318
319
320
321
322
323
324
325
326
327
328
329
330
331
332
333
334
335
336
337
338
339
340
341
342
343
344
345
346
347
348
349
350
351
352
353
354
355
356
357
358
359
360
361
362
363
364
365
366
367
368
369
370
371
372
373
374
375
376
377
378
379
380
381
382
383
384
385
386
387
388
389
390
391
392
393
394
395
600001
600001
600001
600001
600001
600001
600001
600001
600001
600001
600001
600001
600001
600001
600001
600001
600001
600001
600001
600001
600001
600001
600001
600001
600001
10000
10001
10003
10004
10005
10006
10007
501908
501909
600001
600001
600001
600003
600004
600005
600006
600007
600008
600001
600001
600001
600001
4700000
4700001
4700002
4700003
4700004
4700005
4700006
4700007
4700008
4700009
4700010
4700011
600001
""".strip()

TYPOLOGIES = [
    "category",
    "document",
    "geography",
    "legal-instrument",
    "metric",
    "organisation",
    "policy",
    "timetable",
]

DATASETS = DATASET_STR.split("\n")

LOCATIONS = LOCATION_STR.split("\n")

ORGANISATIONS = ORGANISATION_STR.split("\n")

PERIODS = ["current", "historical"]

data_tuples = [
    # DATA, key
    (TYPOLOGIES, "typology"),
    (DATASETS, "dataset"),
    (LOCATIONS, "location"),
    (ORGANISATIONS, "organisation"),
    (PERIODS, "period"),
]

FORMATS = [None, ".json", ".geojson"]
