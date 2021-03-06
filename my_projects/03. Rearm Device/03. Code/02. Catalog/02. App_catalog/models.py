from django.db import models
from django.shortcuts import reverse


def manufacture_img_name(instance, filename):
    return 'manufacture/{0}/img/{1}'.format(instance.slug, filename)


class Manufacture(models.Model):
    name = models.CharField('Название компании', max_length=30)
    slug = models.SlugField('URL производителя', max_length=30, unique=True)
    img = models.ImageField('Логотип компании', upload_to=manufacture_img_name, help_text='500x500px')
    country = models.CharField('Страна производитель', max_length=60)

    def get_absolute_url(self):
        return reverse('manufacture:detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Производитель'
        verbose_name_plural = 'Производители'

def category_img_name(instance, filename):
    return 'category/{0}/img/{1}'.format(instance.slug, filename)


class Category(models.Model):
    name = models.CharField('Название категории', max_length=30)
    slug = models.SlugField('URL категории', max_length=30, unique=True)
    img = models.ImageField('Картинка категории ', upload_to=category_img_name)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:category_detail', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Product(models.Model):
    categories = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    manufacture = models.ForeignKey(Manufacture, on_delete=models.SET_NULL, verbose_name='Производитель', null=True)
    name = models.CharField('Имя товара', max_length=50)
    slug = models.SlugField('URL товара', max_length=30, unique=True, blank=True)
    date = models.DateTimeField('Дата добовления', auto_now_add=True)
    price = models.IntegerField('Цена', help_text='руб.')
    warehouse = models.IntegerField('Количество товара на складе', help_text='шт.')
    warranty = models.IntegerField('Гарантия', help_text='месяцев')
    description = models.TextField('Описание')
    specifications = models.TextField('Характеристики')

    def get_absolute_url(self):
        return reverse('catalog:product_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


def product_img_name(instance, filename):
    return 'products/{0}/img/{1}'.format(instance.products.slug, filename)


class ProductsImage(models.Model):
    products = models.ForeignKey(Product, related_name='prodimg', on_delete=models.CASCADE)
    img = models.ImageField(upload_to=product_img_name)

    class Meta:
        verbose_name = 'Картинка товара'
        verbose_name_plural = 'Картинки товаров'
