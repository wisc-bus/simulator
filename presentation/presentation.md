# Presentation

fix: font size
     better x, y label
     running for whole week of SCanalyzer

[tester_results]:tester_results.png

[perf_short]: perf_short.png
[perf_long]: perf_long.png

[madison_short]: madison_short.png
[madison_long]: madison_long.png
[madison_service]: madison_service.png
[madison_routes]: madison_routes.png
[madison_city_plot]: madison_city_plot.png
[madison_min_service_dist]: madison_min_service_dist.png
[madison_min_service_time]: madison_min_service_time.png
[madison_start_points]: Madison_startpoints.png

[stlouis_short]: stlouis_short.png
[stlouis_long]: stlouis_long.png
[stlouis_routes]: stlouis_routes.jpg
[stlouis_low]: stlouis_low.png
[stlouis_high]: stlouis_high.png
[stlouis_startpoints]: stlouis_startpoints.png

[minneapolis_routes]: minneapolis_routes.png
[minneapolis_short]: minneapolis_short.png
[minneapolis_long]: minneapolis_long.png

[lansing_short]: lansing_short.png
[lansing_long]: lansing_long.png
[lansing_routes]: lansing_routes.jpg

## **Part 1: Code quality improvements**
* Fixes
  * Fixing the hard coded epsg
  * Comments
  * Project structure
* Testing
  * Adding tests to the projects using pytest
    * Mainly tested manually created fake data to make sure project is working
    * running **`pytest tester.py -v --disable-warnings`** in the same folder as testers.py should results:
  ![alt text][tester_results]
* Performance measurements/failed attempts:
  * One attempt is to increase the performance of the original graph search method by utilizing innate sort function from python. However, after the performance test, the original version was found to be better.
    * Below is the graph when the elapse time is short (30min), we can see both version have similar performance
   ![alt text][perf_short]
    * Below is the graph when the elapse time is long (90min), we can see that the original version is much faster
  ![alt text][perf_long]
---
## **Part 2: 4 City Analysis**

### *Madison, Wisconsin*

![alt text][madison_start_points]

|    | label                                   |   max coverage |   min coverage |
|---:|:----------------------------------------|---------------:|---------------:|
|  0 | (43.05863684011441, -89.33164201625276) |        1.44797 |       1.44797  |
|  1 | (43.1447167157741, -89.36849196981703)  |        8.40589 |       8.40589  |
|  2 | (43.13793231162969, -89.35904090074727) |        5.45128 |       5.45128  |
|  3 | (43.10973220461785, -89.35378965001736) |        5.55401 |       5.55401  |
|  4 | (43.11808048149292, -89.35926999648247) |        7.38527 |       7.16769  |
|  5 | (43.08965426447594, -89.51219979010558) |        4.0406  |       0.321148 |
|  6 | (43.12035329229006, -89.36689904070965) |        2.50079 |       2.50079  |

![alt text][madison_routes]
* Above is the madison city routes 
  
![alt text][madison_short]
* Above is the SCanalyzer result graph when given 30 min elapse time:
  * Time to run SCanalyzer: $79.7232$ `sec`
  * Max coverage of **a week**, unit: $km^2$
    * Olbrich Gardens: 31.8504
    * The Nat: 0.9351
    * 330 N Orchard St:  47.3418
  * Min coverage of **a week**, unit: $km^2$
    * Olbrich Gardens: 3.775
    * The Nat: 0
    * 330 N Orchard St:  0.0181
  
![alt text][madison_long]
* 90 min elapsing run:
  * Time to run SCanalyzer: $613.922$ `sec`
  * Max coverage of **a week**, unit: $km^2$
    * Olbrich Gardens: $224.9967$
    * The Nat: $124.0213$
    * 330 N Orchard St:  $264.0516$

  * Min coverage of **a week**, unit: $km^2$
    * Olbrich Gardens: $3.7747$
    * The Nat: $0$
    * 330 N Orchard St: $19.3963$
***
* One interesting fact can be observed is that at **The Nat**, it seems like the bus coverage is relatively small
  ![alt text][madison_city_plot]
* From the graph above we can see that **The Nat** does have a small bubble, which means a small coverage: 

* service graph:
  ![alt text][madison_service]

* Routes with smallest service distance:
  ![alt text][madison_min_service_dist]
* Routes with smallest service time:
  ![alt text][madison_min_service_time]


### *St. Louis, Missouri*
![alt text][stlouis_routes]

![alt text][stlouis_startpoints]

* 30 min run (low) (Time Taken: 72.66282796859741):
![alt text][stlouis_low]

|    | label                                    |   max coverage |   min coverage |
|---:|:-----------------------------------------|---------------:|---------------:|
|  0 | (38.746552975793826, -90.32366958934445) |       21.9341  |              0 |
|  1 | (38.73228422884455, -90.23796506296235)  |       18.5819  |              0 |
|  2 | (38.67320549137285, -90.26337385384753)  |       20.3912  |              0 |
|  3 | (38.62526994097163, -90.10676075888955)  |       15.4586  |              0 |
|  4 | (38.553566414916084, -90.17747677561692) |        5.5337  |              0 |
|  5 | (38.74922605851386, -90.20346081153258)  |       12.2374  |              0 |
|  6 | (38.699066460086975, -90.25582323640651) |        8.60969 |              0 |
|  7 | (38.71368054319952, -90.32688905199662)  |       12.7927  |              0 |
|  8 | (38.61458240297301, -90.27222035993542)  |       10.0945  |              0 |


* 30 min run (high) (Time Taken: 75.69375801086426:
![alt text][stlouis_high]

|    | label                                    |   max coverage |   min coverage |
|---:|:-----------------------------------------|---------------:|---------------:|
|  0 | (38.653449080130734, -90.30491590026699) |        41.4912 |              0 |
|  1 | (38.59105671485263, -90.27665443610043)  |        37.6306 |              0 |
|  2 | (38.6397371209948, -90.33661872147931)   |        15.7728 |              0 |
|  3 | (38.64673791210517, -90.30980061054092)  |        24.3654 |              0 |
|  4 | (38.646968239007855, -90.33532779707863) |        21.7613 |              0 |
|  5 | (38.649533395108314, -90.2968382927907)  |        47.0731 |              0 |

### *Minneapolis, Minnesota*
![alt text][minneapolis_routes]
![alt text][minneapolis_short]
* 30 min run:
  * Time to run SCanalyzer: $499.7719$ 'sec'
  * Max coverage of **Mon,Tues**, unit: $km^2$
    * St John's Child Care & Nursey: $35.1814$
    * Salon On the Edge: $54.0881$
    * Shingle Creek Park:  $20.9968$
  * Min coverage of **Mon,Tues**, unit: $km^2$
    * St John's Child Care & Nursey: $24.8097$
    * Salon On the Edge: $27.1013$
    * Shingle Creek Park:  $1.4757$

![alt text][minneapolis_long]
* 90 min run:
  * Time to run SCanalyzer: $46725.9450$ 'sec'
  * Max coverage of **Mon,Tues**, unit: $km^2$
    * St John's Child Care & Nursey: $568.9084$
    * Salon On the Edge: $881.0581$
    * Shingle Creek Park:  $581.2672$
  * Min coverage of **Mon,Tues**, unit: $km^2$
    * St John's Child Care & Nursey: $414.2151$
    * Salon On the Edge: $542.8334$
    * Shingle Creek Park:  $96.9203$

### *Lansing, Michigan*

* 30 min run (Time Taken: 73.83022403717041):
  * Max coverage of **a week**, unit: $km^2$
    * Michigan State Capitol: $56.001443$
    * Potter Park Zoo: $12.201751$
    * Lansing Christian High School:  $5.780915$
  * Min coverage of **a week**, unit: $km^2$
    * Michigan State Capitol: $23.514244$
    * Potter Park Zoo: $1.470077$
    * Lansing Christian High School:  $0.621025$
![alt text][lansing_short]

* 90 min run (Time Taken: 398.38797783851624):
  * Max coverage of **a week**, unit: $km^2$
    * Michigan State Capitol: $218.005403$
    * Potter Park Zoo: $144.727143$
    * Lansing Christian High School:  $133.52313$
  * Min coverage of **a week**, unit: $km^2$
    * Michigan State Capitol: $14.579151$
    * Potter Park Zoo: $0.056625$
    * Lansing Christian High School:  $15.419283$
![alt text][lansing_long]
