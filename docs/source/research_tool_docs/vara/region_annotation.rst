*****************
Region Annotation
*****************

Region annotations are a pre-step on the compiler front-end side, which allows front-ends to add specific information into LLVM-IR for later analysis.

* Highlight-Regions

With the RegionType ``High`` we can detect highlight regions, a basic region implementation that lets us highlight certain parts of a program.
Take for example the following program.

.. code-block:: cpp

  int main(/* int argc, char *argv[] */) {

    int a = 0;
    ___REGION_START __RT_High "res init"
    int res = 0;
    ___REGION_END __RT_High "res init"
    int b = 0;

    a = 20;
    b = 22;

    ___REGION_START __RT_High "res calc"
    res = a + b;
    ___REGION_END __RT_High "res calc"

    return 0;
  }

Here we mark the result variable and the result calculation to be highlight.
During the AST to LLVM-IR lowering step, Clang adds information to the IR to mark all instructions related to our highlighted areas, allowing us to analyses these instructions further.


.. _commit-regions-annotation:

* Commit-Regions

With the RegionType ``Commit`` we can detect commit regions, specific regions that were previously added by a commit annotation script.

* If-Regions



How-to create your own region annotation
----------------------------------------


1. Teach clang to handle the IRegion annotation

  i. Extend clang/Basic/TokenKinds.def with you region by defining ANNOTATION_REGION(KEYWORD, CLASSNAME). Here KEYWORD is marking the type of the Region, e.g., __RT_High, and CLASSNAME is the name of the region class.

  ii. Create your own Annotation class in RegionStore.h/.cpp with BaseAnnotation as base class. Overwrite the virtual methods. Especially, your class needs to provide two static constexpr fields Name, the refered name of your annotation, which is used to enable the detection with -fvara-handleRA=Name, and AnnoTypeTok, which is your KEYWORD with the ``tok::kw_`` prefix.

2. Implement IRegionDetection in VaRA

  i. Create your own IRegion class, preferably in Regions.h, and implement the basic interface. Furthermore, you need to extend the IRegion kind enum for LLVM-RTTI. (This will be changed in the future to be auto generated)

  ii. Next you can implement a factory method in the IRegionFactory support class to make creating and managing your IRegion easier.

  iii. Last, you need to provide a Detection pass that creates the IRegions from meta data.

For example, you can look at the HighlightAnnotation and HighlightRegion classes, which provide a simple IRegion that allows to highlight certain code regions.
