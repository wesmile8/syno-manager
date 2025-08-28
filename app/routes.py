from syno2.app import db
from syno2.app.models import DiskArray, Tag, StoredFile
from syno2.app.auth import login_required
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
import os
import uuid

bp = Blueprint('main', __name__)


# 辅助函数：检查文件是否允许上传
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


# 辅助函数：转换为基础单位(MB)
def convert_to_mb(size, unit):
    if unit == 'GB':
        return size * 1024
    elif unit == 'TB':
        return size * 1024 * 1024
    return size  # MB


@bp.route('/')
@login_required
def index():
    # 获取所有标签
    tags = Tag.query.all()

    # 获取选中的标签和视图模式
    selected_tag_id = request.args.get('tag_id', type=int)
    view_mode = request.args.get('view', 'card')  # 默认卡片视图

    # 根据标签筛选阵列
    if selected_tag_id:
        tag = Tag.query.get_or_404(selected_tag_id)
        arrays = tag.arrays
    else:
        arrays = DiskArray.query.all()

    return render_template('index.html',
                           arrays=arrays,
                           tags=tags,
                           selected_tag_id=selected_tag_id,
                           view_mode=view_mode)


@bp.route('/array/add', methods=['GET', 'POST'])
@login_required
def add_array():
    if request.method == 'POST':
        # 处理文件上传
        image_paths = []
        if 'images' in request.files:
            files = request.files.getlist('images')
            for file in files:
                if file and allowed_file(file.filename):
                    # 生成唯一文件名
                    filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    image_paths.append(f'uploads/{filename}')

        # 获取单位并转换为MB存储
        size_unit = request.form['size_unit']
        total_size = convert_to_mb(float(request.form['total_size']), size_unit)
        used_size = convert_to_mb(float(request.form['used_size']), size_unit)

        # 创建新阵列
        new_array = DiskArray(
            model=request.form['model'],
            location=request.form['location'],
            sn_code=request.form['sn_code'],
            image_paths=','.join(image_paths) if image_paths else None,
            total_size=total_size,
            used_size=used_size,
            size_unit=size_unit
        )

        # 添加标签
        tag_names = [name.strip() for name in request.form['tags'].split(',') if name.strip()]
        for tag_name in tag_names:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            new_array.tags.append(tag)

        db.session.add(new_array)
        db.session.commit()
        flash('磁盘阵列添加成功', 'success')
        return redirect(url_for('main.index'))

    return render_template('add_array.html')


@bp.route('/array/<int:array_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_array(array_id):
    array = DiskArray.query.get_or_404(array_id)

    if request.method == 'POST':
        # 处理文件上传
        current_images = array.image_list
        if 'images' in request.files:
            files = request.files.getlist('images')
            for file in files:
                if file and allowed_file(file.filename) and file.filename:
                    # 保存新图片
                    filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    current_images.append(f'uploads/{filename}')

        # 处理删除图片请求
        delete_images = request.form.getlist('delete_image')
        if delete_images:
            # 保留未被选中删除的图片
            current_images = [img for img in current_images if img not in delete_images]
            # 删除服务器上的图片文件
            for img in delete_images:
                img_path = os.path.join(current_app.config['UPLOAD_FOLDER'], os.path.basename(img))
                if os.path.exists(img_path):
                    os.remove(img_path)

        # 处理单位转换
        size_unit = request.form['size_unit']
        total_size = convert_to_mb(float(request.form['total_size']), size_unit)
        used_size = convert_to_mb(float(request.form['used_size']), size_unit)

        # 更新阵列信息
        array.model = request.form['model']
        array.location = request.form['location']
        array.sn_code = request.form['sn_code']
        array.image_paths = ','.join(current_images) if current_images else None
        array.total_size = total_size
        array.used_size = used_size
        array.size_unit = size_unit

        # 更新标签
        array.tags = []
        tag_names = [name.strip() for name in request.form['tags'].split(',') if name.strip()]
        for tag_name in tag_names:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            array.tags.append(tag)

        db.session.commit()
        flash('磁盘阵列更新成功', 'success')
        return redirect(url_for('main.index'))

    # 准备标签字符串
    tag_str = ', '.join([tag.name for tag in array.tags])
    return render_template('edit_array.html', array=array, tag_str=tag_str)


@bp.route('/array/<int:array_id>/add_file', methods=['POST'])
@login_required
def add_file(array_id):
    array = DiskArray.query.get_or_404(array_id)

    # 处理文件单位
    file_unit = request.form['file_unit']
    file_size = convert_to_mb(float(request.form['file_size']), file_unit)

    new_file = StoredFile(
        name=request.form['file_name'],
        size=file_size,
        size_unit=file_unit,
        array_id=array_id
    )

    db.session.add(new_file)
    db.session.commit()
    flash('文件信息添加成功', 'success')
    return redirect(url_for('main.index'))


@bp.route('/file/<int:file_id>/delete', methods=['POST'])
@login_required
def delete_file(file_id):
    file = StoredFile.query.get_or_404(file_id)
    array_id = file.array_id
    db.session.delete(file)
    db.session.commit()
    flash('文件已删除', 'info')
    return redirect(url_for('main.index'))


@bp.route('/array/<int:array_id>/delete', methods=['POST'])
@login_required
def delete_array(array_id):
    array = DiskArray.query.get_or_404(array_id)

    # 删除关联的图片
    for img_path in array.image_list:
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'],
                                  os.path.basename(img_path))
        if os.path.exists(image_path):
            os.remove(image_path)

    db.session.delete(array)
    db.session.commit()
    flash('磁盘阵列已删除', 'info')
    return redirect(url_for('main.index'))
