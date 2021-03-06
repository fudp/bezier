Algorithm Helpers
=================

In an attempt to thoroughly vet each algorithm used in this
library, each computation is split into small units that can
be tested independently.

Though many of these computational units aren't provided as part
of the public interface of the Python package, they are still interesting.
(Possibly) more importantly, it's useful to see these algorithms
at work.

In this document, these helper functions and types are documented.
This is to help with the exposition of the computation and
**does not** imply that these are part of the stable public interface.

.. autoclass:: bezier._intersection_helpers.Intersection
   :members:
.. autofunction:: bezier._intersection_helpers._newton_refine
.. autoclass:: bezier._geometric_intersection.Linearization
   :members:
.. autoclass:: bezier._geometric_intersection.SubdividedCurve
   :members:
.. autofunction:: bezier._geometric_intersection.linearization_error
.. autofunction:: bezier._geometric_intersection.segment_intersection
.. autofunction:: bezier._geometric_intersection.parallel_lines_parameters
.. autofunction:: bezier._curve_helpers._get_curvature
.. autofunction:: bezier._curve_helpers._newton_refine
.. autoclass:: bezier._intersection_helpers.IntersectionClassification
   :members:
.. autofunction:: bezier._surface_helpers.classify_intersection
.. autofunction:: bezier._surface_helpers._jacobian_det
.. autofunction:: bezier._surface_intersection._newton_refine
.. autofunction:: bezier._algebraic_intersection.bezier_roots
.. autofunction:: bezier._algebraic_intersection.lu_companion
.. autofunction:: bezier._algebraic_intersection.bezier_value_check

.. |eacute| unicode:: U+000E9 .. LATIN SMALL LETTER E WITH ACUTE
   :trim:
