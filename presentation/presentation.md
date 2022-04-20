# Presentation
[perf_short]: perf_short.png
[perf_long]: perf_long.png

[madison_short]: madison_short.png
[madison_long]: madison_long.png
[madison_service]: madison_service.png
[madison_routes]: madison_routes.png

[stlouis_short]: stlouis_short.png
[stlouis_long]: stlouis_long.png
[stlouis_routes]: stlouis_routes.jpg

[minneapolis_routes]: minneapolis_routes.png
[minneapolis_short]: minneapolis_short.png
[minneapolis_long]: minneapolis_long.png


## **Part 1: Code quality improvements**
* Fixes
  * Fixing the hard coded epsg
  * Comments
  * Project structure
* Testing
  * Adding tests to the projects using pytest
    * Mainly tested manually created fake data to make sure project is working
* Performance measurements/failed attempts:
  * One attempt is to increase the performance of the original graph search method by utilizing innate sort function from python. However, after the performance test, the original version was found to be better.
    * Below is the graph when the elapse time is short (30min), we can see both version have similar performance
   ![alt text][perf_short]
    * Below is the graph when the elapse time is long (90min), we can see that the original version is much faster
  ![alt text][perf_long]
---
## **Part 2: 4 City Analysis**

### *Madison, Wisconsin*
![alt text][madison_routes]
* Above 
![alt text][madison_short]
* 30 min elapsing run:
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
* service graph:
  ![alt text][madison_service]

### *St. Louis, Missouri*
![alt text][stlouis_routes]

![alt text][stlouis_short]
* 30 min run:
  * Max coverage of **a week**, unit: $km^2$
    * Busch Stadium: $51.666879$
    * Saint Louis University: $46.418509$
    * East St Louis Senior High School:  $24.166318$
  * Min coverage of **a week**, unit: $km^2$
    * Busch Stadium: $36.898593$
    * Saint Louis University: $22.212706$
    * East St Louis Senior High School:  $10.964546$
![alt text][stlouis_long]
* 90 min run:
  * Max coverage of **a week**, unit: $km^2$
    * Busch Stadium: $730.063943$
    * Saint Louis University: $660.430581$
    * East St Louis Senior High School:  $521.318002$
  * Min coverage of **a week**, unit: $km^2$
    * Busch Stadium: $635.901999$
    * Saint Louis University: $501.182033$
    * East St Louis Senior High School:  $322.564781$

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