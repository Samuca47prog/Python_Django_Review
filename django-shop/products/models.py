# products/models.py
from __future__ import annotations

from decimal import Decimal
from typing import Optional

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q, F, Index
from django.db.models.functions import Lower
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


# ---------------------------
# Categories (self-FK parent)
# ---------------------------
class Category(models.Model):
    name = models.CharField(max_length=80)
    slug = models.SlugField(max_length=100)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.PROTECT,  # prevent deleting a parent while it has children/products
    )

    class Meta:
        ordering = ["name"]
        indexes = [
            Index(fields=["parent", "slug"], name="cat_parent_slug_idx"),
        ]
        constraints = [
            # Unique slug within the same parent (case-insensitive)
            models.UniqueConstraint(
                Lower("slug"), "parent", name="cat_unique_slug_per_parent_ci"
            ),
            # Disallow self-parenting (simple sanity)
            models.CheckConstraint(
                check=~Q(parent=F("id")), name="cat_no_self_parent"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.parent} > {self.name}" if self.parent_id else self.name

    def get_absolute_url(self) -> str:
        return reverse("products:category", kwargs={"slug": self.slug})


# -----
# Tags
# -----
class Tag(models.Model):
    name = models.CharField(max_length=40)
    slug = models.SlugField(max_length=60)

    class Meta:
        ordering = ["name"]
        indexes = [Index(fields=["slug"], name="tag_slug_idx")]
        constraints = [
            models.UniqueConstraint(Lower("name"), name="tag_name_ci_unique"),
            models.UniqueConstraint(Lower("slug"), name="tag_slug_ci_unique"),
        ]

    def __str__(self) -> str:
        return self.name


# -----------------
# Product & helpers
# -----------------
class ProductStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"
    ARCHIVED = "archived", "Archived"


class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def published(self):
        return self.filter(status=ProductStatus.PUBLISHED, is_active=True)

    def search(self, q: Optional[str]):
        if not q:
            return self
        return self.filter(Q(name__icontains=q) | Q(description__icontains=q))


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        related_name="products",
        on_delete=models.PROTECT,  # keep referential integrity
    )

    name = models.CharField(max_length=120)
    # We enforce uniqueness *conditionally* (only for active rows) via a DB constraint,
    # so we do NOT set unique=True on the field itself.
    slug = models.SlugField(max_length=140, blank=True)

    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    is_active = models.BooleanField(default=True)
    status = models.CharField(
        max_length=16, choices=ProductStatus.choices, default=ProductStatus.DRAFT
    )
    published_at = models.DateTimeField(null=True, blank=True, default=None)

    # M2M via explicit through table (adds constraints + extra fields)
    tags = models.ManyToManyField(
        Tag, through="ProductTag", related_name="products", blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)  # set on INSERT
    updated_at = models.DateTimeField(auto_now=True)      # set on UPDATE

    objects = ProductQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            Index(fields=["slug"], name="product_slug_idx"),
            Index(fields=["-created_at"], name="product_created_idx"),
            Index(fields=["category", "-created_at"], name="product_category_created_idx"),
        ]
        constraints = [
            # Ensure non-negative price (redundant with validator, but enforced at DB-level)
            models.CheckConstraint(check=Q(price__gte=0), name="product_price_gte_0"),
            # Case-insensitive, conditional uniqueness for active products
            models.UniqueConstraint(
                Lower("name"),
                condition=Q(is_active=True),
                name="product_name_ci_unique_active",
            ),
            models.UniqueConstraint(
                Lower("slug"),
                condition=Q(is_active=True),
                name="product_slug_ci_unique_active",
            ),
        ]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        # Adjust to whatever URL you wired for product detail
        return reverse("products:detail", kwargs={"slug": self.slug})

    # --- Domain methods ---
    def publish(self):
        if self.status != ProductStatus.PUBLISHED:
            self.status = ProductStatus.PUBLISHED
            self.published_at = self.published_at or timezone.now()
            self.save(update_fields=["status", "published_at", "updated_at"])

    # --- Internal helpers ---
    def _ensure_slug(self):
        if self.slug or not self.name:
            return
        base = slugify(self.name) or "product"
        slug = base
        i = 2
        # Only ensure uniqueness among *active* rows (matching our constraint)
        while Product.objects.filter(slug=slug, is_active=True).exclude(pk=self.pk).exists():
            slug = f"{base}-{i}"
            i += 1
        self.slug = slug

    def save(self, *args, **kwargs):
        self._ensure_slug()
        if self.status == ProductStatus.PUBLISHED and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)


# --------------------------
# Through table: ProductTag
# --------------------------
class ProductTag(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    weight = models.PositiveSmallIntegerField(default=1)  # example extra field
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "tag"], name="product_tag_unique"
            ),
            models.CheckConstraint(
                check=Q(weight__gte=1), name="producttag_weight_gte_1"
            ),
        ]
        indexes = [
            Index(fields=["product", "tag"], name="product_tag_idx"),
            Index(fields=["tag", "product"], name="tag_product_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.product} ↔ {self.tag} (w={self.weight})"
