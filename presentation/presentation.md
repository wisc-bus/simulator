# Presentation
---
[perf_short]: perf_short.png
[perf_long]: perf_long.png
<!-- [madison_short]:  -->
[stlouis_short]: stlouis_short.png
[stlouis_long]: stlouis_long.png

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

* 90 min run:
  * Max coverage of **a week**, unit: $km^2$
    * Busch Stadium: $730.063943$
    * Saint Louis University: $660.430581$
    * East St Louis Senior High School:  $521.318002$
![alt text][stlouis_short]
  * Min coverage of **a week**, unit: $km^2$
    * Busch Stadium: $635.901999$
    * Saint Louis University: $501.182033$
    * East St Louis Senior High School:  $322.564781$
![alt text][stlouis_long]


### *Minneapolis, Minnesota*

### *Lansing, Michigan*