"""

Volume

"""
import boto3
import cellprofiler.image
import cellprofiler.measurement
import cellprofiler.module
import cellprofiler.setting
import re
import skimage.io


class AmazonS3(cellprofiler.module.Module):
    category = "File Processing"
    module_name = "Amazon S3"
    variable_revision_number = 1

    def is_3d_load_module(self):
        return True

    def create_settings(self):
        self.url = cellprofiler.setting.PathnameOrURL(
            "URL"
        )

        self.name = cellprofiler.setting.ImageNameProvider(
            text="Name"
        )

    def settings(self):
        return [
            self.url,
            self.name
        ]

    def visible_settings(self):
        return [
            self.url,
            self.name
        ]

    def prepare_run(self, workspace):
        # Pipeline counts image sets from measurements.image_set_count and will raise an error if there are no image
        # sets (which is apparently the same as no measurements).
        workspace.measurements.add_measurement(
            cellprofiler.measurement.IMAGE,
            cellprofiler.measurement.C_PATH_NAME,
            self.url.value
        )

        return True

    def run(self, workspace):
        path = self.url.value

        name = self.name.value

        client = boto3.client('s3')

        bucket_name, filename = re.compile('s3://([\w\d\-\.]+)/(.*)').search(path).groups()

        url = client.generate_presigned_url('get_object',
                                            Params={'Bucket': bucket_name, 'Key': filename,},
                                            ExpiresIn=86400, )

        x = skimage.io.imread(url)

        image = cellprofiler.image.Image()

        image.pixel_data = x

        workspace.image_set.add(name, image)

        if self.show_window:
            workspace.display_data.image = x

    def display(self, workspace, figure):
        figure.set_subplots((1, 1))

        figure.subplot_imshow_grayscale(
            0,
            0,
            workspace.display_data.image
        )
