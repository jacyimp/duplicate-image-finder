import beeprint as beeprint

from imageSimilarity import ImageSimilarity

sim = ImageSimilarity()
sim.add_image_directory("E:/sorted/9")
beeprint.pp(sim.find_dupes())
