Image sorting

idea: present 2 images, choose the best one. Repeat till all images are sorted by preference
challenges/ideas:
which two images to compare at each step?
can just plug into standard sorting algorithms?
How to ensure an amount of diversity in the results? (dont want 10 versions of the same shot to be the winner)

time complexity:
baby photos album currently has 600 photos. Guick sort has average execution time of n * log(n) = 600 * log(600) = 1666 comparisons. This seems like too many.
Note - goal is to quickly filter the best, say, 10%. Having every single image in exact preference order is not so important.
Idea: single elimination tournament? https://en.wikipedia.org/wiki/Single-elimination_tournament
Would not gaurantee best images make it to top, but might do a good enough job of sorting. Could run multiple rounds to improve ordering
Paper about tournaments: https://pdfs.semanticscholar.org/fbbe/c77915dc20173a96a917e60783df60def51f.pdf


goal is to quickly find the best, say, 10% of images - not nec