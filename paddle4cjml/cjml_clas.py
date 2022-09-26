from paddleclas import PaddleClas


class CjmlClas:
    def __init__(self, inference_model_dir='clas_infer_18', top_k=1):
        """
        初始化一个分类器

        :param inference_model_dir: 推理模型文件夹
        :param top_k: 预测的top数
        """
        self.clas = PaddleClas(inference_model_dir=inference_model_dir, topk=top_k)

    def get_image_class(self, image_path):
        """
        根据图片的路径获取图片的分类结果

        :param image_path: 图片路径
        :return: 图片分类结果id
        """
        if image_path[-5: -4] == '本':
            return
        result = self.clas.predict(image_path)
        return next(result)[0]['class_ids'][0]

    def get_image_top2_class_and_score(self, image_path):
        """
        根据图片的路径获取图片的top2分类结果和置信度

        :param image_path: 图片路径
        :return: 图片分类结果top2
        """
        if image_path[-5: -4] == '本':
            return
        result = self.clas.predict(image_path)
        res_dict = next(result)[0]
        top2_class_and_score = [res_dict['class_ids'], res_dict['scores']]
        return top2_class_and_score


def start_clas(save_clas_dir, max_size):
    clas = CjmlClas()
    clas_res = clas.get_image_class("https://cjml.oss-cn-shanghai.aliyuncs.com/appvin/vin_ios_1655965806676_7080.jpg")
    print(clas_res)


if __name__ == '__main__':
    # cls = CjmlClas(top_k=2)
    # res = cls.get_image_top2_class_and_score(r'D:\wjs\clas_data_set\eval_data\4045\3C4PDCGB7GT236220-vin_ios_1641283583267_45445.jpg')
    # print(abs(45 - 90))

    res_dir = "clas"
    size = 5000
    start_clas(dir, size)
