import datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import Address
from apps.catalog.models import Category, Product, Review
from apps.orders.models import Coupon

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds the database with curated categories, products, reviews, coupons, and a demo customer."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding AuraStore database..."))

        # 1. Create Demo Customer
        demo_user, created = User.objects.get_or_create(
            username="democustomer",
            defaults={
                "email": "customer@aurastore.com",
                "first_name": "Elena",
                "last_name": "Vance",
                "phone": "+15553498821",
            },
        )
        if created:
            demo_user.set_password("Password123!")
            demo_user.save()
            self.stdout.write(
                self.style.SUCCESS(f"Created demo user: {demo_user.email}")
            )

        # Create Saved Address
        Address.objects.get_or_create(
            user=demo_user,
            address="742 Evergreen Terrace",
            city="Denver",
            postal_code="80202",
            country="United States",
            defaults={
                "full_name": "Elena Vance",
                "phone": "+15553498821",
                "is_default": True,
            },
        )

        # 2. Create Categories
        categories_data = [
            {
                "name": "Audio & Acoustic",
                "slug": "audio",
                "description": "Audiophile studio headphones, lossless monitors, and wireless sound.",
            },
            {
                "name": "Timepieces & Watches",
                "slug": "watches",
                "description": "Minimalist mechanical and quartz horology engineered for precision.",
            },
            {
                "name": "Leather & Essentials",
                "slug": "leather-goods",
                "description": "Hand-stitched vegetable-tanned leather folios, wallets, and straps.",
            },
            {
                "name": "Living & Objects",
                "slug": "living",
                "description": "Calm architectural homeware, ceramic vessels, and artisanal desk objects.",
            },
            {
                "name": "Apparel & Outerwear",
                "slug": "apparel",
                "description": "Technical fabrics, restrained silhouettes, and sustainable organic cotton.",
            },
        ]

        cats = {}
        for cdata in categories_data:
            cat, _ = Category.objects.get_or_create(
                slug=cdata["slug"],
                defaults={
                    "name": cdata["name"],
                    "description": cdata["description"],
                    "is_active": True,
                },
            )
            cats[cdata["slug"]] = cat

        # 3. Create Curated Products
        products_data = [
            {
                "category": cats["audio"],
                "name": "Aura Studio Planar Headphones",
                "slug": "aura-studio-planar-headphones",
                "description": "Open-back planar magnetic transducers delivering expansive spatial staging and transparent acoustic fidelity. Crafted with aircraft-grade aluminum and memory foam velour pads.",
                "price": Decimal("399.00"),
                "sku": "AURA-AUD-001",
                "stock": 18,
                "featured": True,
            },
            {
                "category": cats["audio"],
                "name": "Linear Soundbar 01",
                "slug": "linear-soundbar-01",
                "description": "Compact monolithic soundbar featuring custom beryllium drivers, active room calibration, and lossless Wi-Fi / AirPlay 2 streaming.",
                "price": Decimal("249.50"),
                "sku": "AURA-AUD-002",
                "stock": 12,
                "featured": False,
            },
            {
                "category": cats["watches"],
                "name": "Monochrome Automatic 38mm",
                "slug": "monochrome-automatic-38mm",
                "description": "Three-hand automatic mechanical timepiece with matte exhibition dial, double-domed anti-reflective sapphire crystal, and 42-hour power reserve.",
                "price": Decimal("480.00"),
                "sku": "AURA-WAT-001",
                "stock": 9,
                "featured": True,
            },
            {
                "category": cats["watches"],
                "name": "Field Chronograph Titanium",
                "slug": "field-chronograph-titanium",
                "description": "Grade-5 sandblasted titanium casing with screw-down crown, high-beat meca-quartz movement, and luminescent indices for extreme environments.",
                "price": Decimal("320.00"),
                "sku": "AURA-WAT-002",
                "stock": 14,
                "featured": False,
            },
            {
                "category": cats["leather-goods"],
                "name": "Vegetable-Tanned Daily Brief",
                "slug": "vegetable-tanned-daily-brief",
                "description": "Full-grain Tuscan bridle leather carrying case designed for 16-inch laptops, documents, and daily writing implements with custom brass hardware.",
                "price": Decimal("340.00"),
                "sku": "AURA-LEA-001",
                "stock": 7,
                "featured": True,
            },
            {
                "category": cats["leather-goods"],
                "name": "Card Sleeve No. 3",
                "slug": "card-sleeve-no-3",
                "description": "Ultra-slim 3-pocket card holder burnished with natural beeswax and lined with RFID-shielding woven lining.",
                "price": Decimal("65.00"),
                "sku": "AURA-LEA-002",
                "stock": 35,
                "featured": False,
            },
            {
                "category": cats["living"],
                "name": "Basalt Stoneware Pour-Over",
                "slug": "basalt-stoneware-pour-over",
                "description": "Hand-thrown volcanic clay dripper with ribbed extraction channels and heat-retentive unglazed exterior.",
                "price": Decimal("75.00"),
                "sku": "AURA-OBJ-001",
                "stock": 22,
                "featured": True,
            },
            {
                "category": cats["living"],
                "name": "Cast Bronze Paperweight",
                "slug": "cast-bronze-paperweight",
                "description": "Solid sculpted bronze desk object with patinated finish that ages gracefully with touch and atmospheric exposure.",
                "price": Decimal("90.00"),
                "sku": "AURA-OBJ-002",
                "stock": 15,
                "featured": False,
            },
            {
                "category": cats["apparel"],
                "name": "Merino Heavyweight Overshirt",
                "slug": "merino-heavyweight-overshirt",
                "description": "100% Australian extra-fine merino wool woven in a dense 420gsm twill. Naturally thermoregulating, wrinkle-resistant, and weather-shedding.",
                "price": Decimal("210.00"),
                "sku": "AURA-APP-001",
                "stock": 16,
                "featured": True,
            },
        ]

        created_products = []
        for pdata in products_data:
            p, _ = Product.objects.get_or_create(
                slug=pdata["slug"],
                defaults=pdata,
            )
            created_products.append(p)

        # 4. Create Sample Reviews
        sample_reviews = [
            {
                "product": created_products[0],
                "user": demo_user,
                "rating": 5,
                "title": "A masterclass in acoustic engineering",
                "comment": "The clarity of the midrange and the natural, effortless instrument separation are unmatched in this price bracket. Beautiful build quality.",
                "is_verified_purchase": True,
            },
            {
                "product": created_products[2],
                "user": demo_user,
                "rating": 5,
                "title": "Clean, understated perfection",
                "comment": "Wears remarkably well on a 6.75 inch wrist. The dial legibility is wonderful and the case brushing catches the light subtly.",
                "is_verified_purchase": True,
            },
            {
                "product": created_products[4],
                "user": demo_user,
                "rating": 4,
                "title": "Exceptional leather, will patina nicely",
                "comment": "Rigid out of the box as expected with genuine vegetable tan, but softening up after just two weeks of daily commutes.",
                "is_verified_purchase": True,
            },
        ]

        for rdata in sample_reviews:
            Review.objects.get_or_create(
                product=rdata["product"],
                user=rdata["user"],
                defaults={
                    "rating": rdata["rating"],
                    "title": rdata["title"],
                    "comment": rdata["comment"],
                    "is_verified_purchase": rdata["is_verified_purchase"],
                },
            )

        # 5. Create Promotional Coupons
        now = timezone.now()
        one_year_later = now + datetime.timedelta(days=365)

        coupons_data = [
            {
                "code": "WELCOME10",
                "discount_type": Coupon.DISCOUNT_TYPE_PERCENT,
                "discount_value": Decimal("10.00"),
                "min_purchase_amount": Decimal("0.00"),
                "valid_from": now,
                "valid_to": one_year_later,
                "usage_limit": 1000,
                "is_active": True,
            },
            {
                "code": "SAVE20",
                "discount_type": Coupon.DISCOUNT_TYPE_PERCENT,
                "discount_value": Decimal("20.00"),
                "min_purchase_amount": Decimal("100.00"),
                "valid_from": now,
                "valid_to": one_year_later,
                "usage_limit": 500,
                "is_active": True,
            },
            {
                "code": "FLAT25",
                "discount_type": Coupon.DISCOUNT_TYPE_FIXED,
                "discount_value": Decimal("25.00"),
                "min_purchase_amount": Decimal("150.00"),
                "valid_from": now,
                "valid_to": one_year_later,
                "usage_limit": 200,
                "is_active": True,
            },
        ]

        for cpdata in coupons_data:
            Coupon.objects.get_or_create(
                code=cpdata["code"],
                defaults=cpdata,
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully seeded {len(categories_data)} categories, {len(products_data)} products, "
                f"{len(sample_reviews)} reviews, and {len(coupons_data)} promotional coupons!"
            )
        )
