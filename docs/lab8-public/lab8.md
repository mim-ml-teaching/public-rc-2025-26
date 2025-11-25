---
title: Lab 8
usemathjax: true
---

<script type="text/javascript" id="MathJax-script" async
  src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js">
</script>

# Goals

Today’s lab contains two self-contained Colab intros.

## Neural Radiance Fields (NeRF)

[Link to the colab notebook.](https://colab.research.google.com/drive/1TppdSsLz8uKoNwqJqDGg8se8BHQcvg_K?usp=sharing)

A (non-comprehensive) list of questions you might want to ask yourself:

1. Why does taking the last column of the rotation matrix give us the direction for a given view? (Origins and Directions section)
2. Explain how the function `get_rays` works:
 - How do we get ray directions from pixel values?
 - What happens here: `rays_d = torch.sum(directions[..., None, :] * c2w[:3, :3], dim=-1)`?
 - What does the line `rays_o = c2w[:3, -1].expand(rays_d.shape)` do?
3. Review what stratified sampling is. Why might we want to use `inverse_depth=True`?
4. What do we want to achieve with the `sample_hierarchical` function? Why might it be important?


## Kalman filter

[Link to the colab notebook.](https://colab.research.google.com/drive/1XaFlJLMGwd9_0ZwDuyAhGD5yhMG7mzwV?usp=sharing)

We’ll build on the Kalman material and explore this topic further in the subsequent labs and lectures.
