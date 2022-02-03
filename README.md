# duplicate-image-finder
A quick and dirty solution to all your dataset deduplication preprocess needs.
``
#Install
`pip install -r requirements.txt`

#Usage
## Simple
### Finding duplicates in a directory
Set recursive as False.
```python
from imageSimilarity import ImageSimilarity

sim = ImageSimilarity()
sim.add_image_directory("C:/datasets/sample_dir", recursive=False)
print(sim.find_dupes())
```

### Finding duplicates in a directory and subdirectories recursively
Set recursive as True.
```python
from imageSimilarity import ImageSimilarity

sim = ImageSimilarity()
sim.add_image_directory("C:/datasets/sample_dir", recursive=True)
print(sim.find_dupes())
```

### Finding duplicates in a directory and subdirectories recursively with low similarity
`similarity` rate is between 0.0 and 1.0
```python
from imageSimilarity import ImageSimilarity

sim = ImageSimilarity()
sim.add_image_directory("C:/datasets/sample_dir", recursive=True)
print(sim.find_dupes(min_similarity=0.5))
```


**More examples will be available in the `examples` directory.**