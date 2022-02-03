import os
from PIL import Image
from imagehash import average_hash
from numpy import count_nonzero
from tqdm import tqdm
from math import pow


class ImageSimilarity:

    def __init__(self, image_paths: list[str] = None, hash_size: int = 64):
        """
        Arguments:
            :param image_paths: Absolute path to image files. Use add_image_directory() to add folders.
            :param hash_size: Hash size. Bigger, more accurate, less performant.
        """
        self.hashes: list[list[int]] = []
        self.bad_images: list[str] = []
        self.hash_size = hash_size
        if image_paths is not None:
            self.img_paths: list[str] = image_paths
            self.__calculate_hashes()
        else:
            self.img_paths = []

    def add_image_dir(self, additive_path: list[str]):
        """
            Add another image directory and append their hashes to this instance. Performant!
        :param additive_path: List of img directories
        """
        self.img_paths += additive_path
        self.__calculate_hashes(clear_arrays=False)

    def add_image_directory(self, directory_path: str, recursive: bool = True):
        accepted_exts = ['bmp', 'gif', 'jpg', 'jpeg', 'png']
        for file_name in os.listdir(directory_path):
            file_path = os.path.join(directory_path, file_name)
            if os.path.isfile:
                index = file_name.rfind('.')
                ext = file_name[index + 1:].lower()
                if ext in accepted_exts:
                    self.img_paths += [file_path]
            elif recursive:
                self.add_image_directory(file_path, recursive)

        self.__calculate_hashes(clear_arrays=False)

    def change_image_paths(self, new_paths: list[str]):
        """
            Change path to images. Will recalculate hashes.
        :param new_paths: New directory of images.
        """
        self.img_paths: list[str] = new_paths
        self.__calculate_hashes()

    def change_hash_size(self, new_hash_size: int = 64):
        """
            Change hash size of this instance. Will recalculate hashes afterwards.
        :param new_hash_size: New hash size. Bigger = Less performant = More accurate
        """
        self.hash_size = new_hash_size
        self.__calculate_hashes()

    def find_dupes(self, min_similarity: float = 0.8) -> list[str]:
        """
            Find duplicate image files.
        Arguments:
            :param min_similarity: Minimum similarity required. Range [0-1]
            :return: List of [img1, img2, similarity]
        """
        if len(self.img_paths) != len(self.hashes):
            print("Bad config! Incorrect number of hashes and files.")
            return []
        res: list[str, str, float] = []
        dupes: list[int] = []
        for xInd, xHash in enumerate(self.hashes[:-1]):
            for yInd, yHash in enumerate(self.hashes[xInd+1:], start=xInd+1):
                if yInd not in dupes:
                    similarity = self.__calc_similarity(xHash, yHash)
                    if similarity >= min_similarity:
                        dupes += [yInd]
                        res += [[self.img_paths[xInd], self.img_paths[yInd], similarity]]
        return res

    def __calc_similarity(self, x_hash: list[int], y_hash: list[int]) -> float:
        return 1.0 - float(count_nonzero(x_hash != y_hash)) / float(self.hash_size)

    def find_most_similar(self, img_path: str) -> str:
        """
            Find the most similar image among instance's images
        :param img_path: Any image path
        :return: Empty list if image could not be opened, otherwise path to the most similar img
        """
        curHash, was_ok = self.calculate_hash(img_path)
        if was_ok:
            return self.find_most_similar_hash(curHash)[1]
        return ""

    def find_most_similar_hash(self, x_hash: list[int]) -> (list[int], str):
        """
            Find the most similar hash among instance's images
        :param x_hash: Any hash
        :return: Most similar Hash, and path of image
        """
        min_diff: float = -1.0
        best_hash: list[int] = []
        best_path: str = ""
        for yInd, yHash in enumerate(self.hashes):
            similarity = self.__calc_similarity(x_hash, yHash)
            if similarity >= min_diff:
                min_diff = similarity
                best_hash = yHash
                best_path = self.img_paths[yInd]
        return best_hash, best_path

    def order_by_similarity(self) -> list[str]:
        """
            Reorder image paths based on their similarity
        :return: Path of images, ordered by similarity.
        """
        self.hashes: list[list[int]] = []
        img_paths = self.img_paths
        hashes = self.hashes
        ordered_imgs = []
        ordered_imgs += [img_paths.pop(0)]
        prev_hash = hashes.pop(0)
        pbar = tqdm(total=len(hashes))
        while len(img_paths) > 0:
            pbar.update(1)
            min_diff = pow(2, self.hash_size) + 1
            min_diff_idx = ""
            for idx, fy in enumerate(img_paths):
                cur_diff = count_nonzero(prev_hash != hashes[idx])
                if cur_diff < min_diff:
                    min_diff = cur_diff
                    min_diff_idx = idx

            ordered_imgs += [img_paths.pop(min_diff_idx)]
            prev_hash = hashes.pop(min_diff_idx)
        return ordered_imgs

    def find_uniques(self, min_similarity: float = 0.8) -> list[str]:
        dupes = self.find_dupes(min_similarity)
        uniques = []
        for img in self.img_paths:
            cur_is_dupe = False
            for dupe in dupes:
                if dupe[0] == img or dupe[1] == img:
                    cur_is_dupe = True
                    break
            if not cur_is_dupe:
                uniques += [img]
        return uniques

    def __calculate_hashes(self, clear_arrays=True) -> None:
        """
            Calculates hashes for self.img_paths
        :param clear_arrays Whether to clear everything and start over, or continue.
        :return: None
        """
        if clear_arrays:
            self.hashes: list[list[int]] = []
            self.bad_images: list[str] = []
        pbar = tqdm(total=len(self.img_paths) - len(self.hashes), desc="Calculating hashes...")
        for idx, fy in enumerate(self.img_paths[len(self.hashes):]):
            pbar.update(1)
            curHash, was_ok = self.calculate_hash(fy)
            if not was_ok:
                self.bad_images += fy
            pbar.set_postfix({"Bad": len(self.bad_images)}, False)
            self.hashes += [curHash]
        return

    def calculate_hash(self, img_path: str) -> (list[list[int]], bool):
        """
            Calculate the hash for an image
        :param img_path: Image path
        :return: str Hash, and `was-image-okay` bool
        """
        try:
            with Image.open(img_path) as imgy:
                return average_hash(imgy, hash_size=self.hash_size).hash, True
        except:
            return [[0] for _ in range(self.hash_size)], False
