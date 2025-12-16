from odoo import models, fields

class BlogPost(models.Model):
    _inherit = 'blog.post'

    # Ajout d'un champ image simple pour faciliter l'affichage dans votre design custom
    image_preview = fields.Image("Image Aperçu", max_width=1024, max_height=1024, help="Image utilisée sur la page d'accueil du blog marketplace")