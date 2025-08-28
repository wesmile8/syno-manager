from ..app import db
from datetime import datetime

# 标签模型
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    arrays = db.relationship('DiskArray', secondary='array_tag', back_populates='tags')

    def __repr__(self):
        return f'<Tag {self.name}>'


# 磁盘阵列模型
class DiskArray(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(100), nullable=False)  # 阵列型号
    location = db.Column(db.String(100))  # 阵列位置
    sn_code = db.Column(db.String(100))  # 机器码/SN码
    image_paths = db.Column(db.Text)  # 改为多图片路径，用逗号分隔
    total_size = db.Column(db.Float)  # 总大小(基础单位：MB)
    used_size = db.Column(db.Float)  # 已使用大小(基础单位：MB)
    size_unit = db.Column(db.String(10), default='GB')  # 存储单位
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tags = db.relationship('Tag', secondary='array_tag', back_populates='arrays')
    files = db.relationship('StoredFile', backref='array', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<DiskArray {self.model}>'

    @property
    def display_total_size(self):
        """根据单位显示总容量"""
        if self.size_unit == 'GB':
            return round(self.total_size / 1024, 2)
        elif self.size_unit == 'TB':
            return round(self.total_size / (1024 * 1024), 2)
        return round(self.total_size, 2)

    @property
    def display_used_size(self):
        """根据单位显示已使用容量"""
        if self.size_unit == 'GB':
            return round(self.used_size / 1024, 2)
        elif self.size_unit == 'TB':
            return round(self.used_size / (1024 * 1024), 2)
        return round(self.used_size, 2)

    @property
    def usage_percentage(self):
        """计算使用率"""
        if self.total_size and self.used_size:
            return round((self.used_size / self.total_size) * 100, 2)
        return 0

    @property
    def image_list(self):
        """返回图片路径列表"""
        if self.image_paths:
            return self.image_paths.split(',')
        return []


# 存储的文件模型
class StoredFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)  # 文件名
    size = db.Column(db.Float)  # 文件大小(基础单位：MB)
    size_unit = db.Column(db.String(10), default='MB')  # 文件单位
    array_id = db.Column(db.Integer, db.ForeignKey('disk_array.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<StoredFile {self.name}>'

    @property
    def display_size(self):
        """根据单位显示文件大小"""
        if self.size_unit == 'GB':
            return round(self.size / 1024, 2)
        elif self.size_unit == 'TB':
            return round(self.size / (1024 * 1024), 2)
        return round(self.size, 2)


# 阵列-标签关联表
array_tag = db.Table('array_tag',
                     db.Column('array_id', db.Integer, db.ForeignKey('disk_array.id'), primary_key=True),
                     db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
                     )
