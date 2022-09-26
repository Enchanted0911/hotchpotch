import ppdet


class CjmlDetection:
    """
    检测模型
    """

    category2angle = {0: 1000, 1: 3000, 2: 4000, 3: 4045, 4: 4090
                      , 5: 4135, 6: 4180, 7: 4225, 8: 4270, 9: 4315}

    def __init__(self, config='det_infer/beta/beta.yml', weight='det_infer/best_model.pdparams'):
        """
        初始化一个检测模型

        :param config: 检测模型配置文件路径
        :param weight: 检测模型评估模型路径，注意不是推理模型
        """
        self.cfg = ppdet.core.workspace.load_config(config)
        self.trainer = ppdet.engine.Trainer(self.cfg, mode='test')
        self.trainer.load_weights(weight)

    def get_location(self, image_path):
        """
        根据图片路径获取该图片的检测结果

        :param image_path: 待检测的图片路径
        :return: 检测结果的坐标信息
        """
        return self.trainer.predict([image_path])[0]

    def get_location_and_category_id(self, image_path):
        """
        根据图片路径获取该图片的检测结果

        :param image_path: 待检测的图片路径
        :return: 检测结果的坐标信息
        """
        return self.trainer.predict([image_path])


if __name__ == '__main__':
    det = CjmlDetection()
    location = det.get_location('D:\\wjs\\PycharmProjects\\end2end_eval\\eval_e1_it6_add_det_2\\add_det_all_det_des\\INVALID_VIN-vin_android_1646723163821_4472b68e68ee438ea6591ec9db01e986.jpg')

