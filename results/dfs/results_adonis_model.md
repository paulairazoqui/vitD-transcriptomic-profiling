from RStudio:
``` R 
> adonis_model
Permutation test for adonis under reduced model
Marginal effects of terms
Permutation: free
Number of permutations: 999

adonis2(formula = dist_obj ~ cell_id + pert_id, data = permanova_metadata, permutations = 999, by = "margin")
          Df SumOfSqs      R2      F Pr(>F)    
cell_id    4   229602 0.07219 5.0423  0.001 ***
pert_id   11   185216 0.05823 1.4791  0.001 ***
Residual 242  2754852 0.86614                  
Total    257  3180624 1.00000                  
---
Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1
```