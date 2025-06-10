# Create your models here.
# your_app/models.py
from django.db import models

class CountRecord(models.Model):
    # 前端传递的 EIcount 数值（整数值，根据需求可改为 FloatField）
    EIcount = models.IntegerField(verbose_name="EI计数")
    # 前端传递的 EOcount 数值
    EOcount = models.IntegerField(verbose_name="EO计数")
    # 自动记录数据创建时间（可选）
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "计数记录"
        verbose_name_plural = "计数记录"
        ordering = ["-created_at"]  # 按创建时间倒序排列

    def __str__(self):
        return f"EI:{self.EIcount}, EO:{self.EOcount} @ {self.created_at}"
