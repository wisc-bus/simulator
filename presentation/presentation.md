# Presentation
---
[perf_short]: perf_short.png
[perf_long]: perf_long.png
<!-- [madison_short]:  -->
[stlouis_short]: stlouis_short.png
[stlouis_long]: stlouis_long.png
[lansing_short]: lansing_short.png
[lansing_long]: lansing_long.png

---
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

### *St. Louis, Missouri*

* 30 min run (Time Taken: 75.3187210559845):
  * Max coverage of **a week**, unit: $km^2$
    * Busch Stadium: $51.666879$
    * Saint Louis University: $46.418509$
    * East St Louis Senior High School:  $24.166318$
  * Min coverage of **a week**, unit: $km^2$
    * Busch Stadium: $36.898593$
    * Saint Louis University: $22.212706$
    * East St Louis Senior High School:  $10.964546$
![alt text][stlouis_short]

* 90 min run (Time Taken: 474.52902388572693):
  * Max coverage of **a week**, unit: $km^2$
    * Busch Stadium: $730.063943$
    * Saint Louis University: $660.430581$
    * East St Louis Senior High School:  $521.318002$
  * Min coverage of **a week**, unit: $km^2$
    * Busch Stadium: $635.901999$
    * Saint Louis University: $501.182033$
    * East St Louis Senior High School:  $322.564781$
![alt text][stlouis_long]


### *Minneapolis, Minnesota*

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