#!/usr/bin/env python3
"""
Enrichit les pages en thin content (Ubersuggest: content_count_words) en ajoutant
des sections H2 qualité. Respecte la règle: AUCUNE page supprimée, on enrichit.
Usage: python3 scripts/enrich_pages.py
"""
import pathlib, re

ROOT = pathlib.Path("/Users/aymarmichel/bouddhas-site")

# Contenu d'enrichissement par page (slug -> sections H2 à ajouter avant </article> ou fin)
ENRICH = {
    "philosophie": [
        ("<h2>Le karma : la loi de cause à effet</h2>",
         "<p>Au cœur de la philosophie bouddhiste se trouve le <strong>karma</strong>, la loi de cause à effet. Chaque action — physique, verbale ou mentale — produit une conséquence qui façonne nos expériences présentes et futures. Comprendre le karma invite à la responsabilité : nous sommes les auteurs de notre propre liberté.</p>"),
        ("<h2>La compassion (karuna) et l'amour bienveillant (metta)</h2>",
         "<p>La <strong>compassion</strong> n'est pas une simple émotion, mais une posture active envers la souffrance d'autrui. Couplée à la bienveillance (metta), elle constitue le moteur de la pratique bouddhiste et l'antidote de l'égoïsme.</p>"),
        ("<h2>Le détachement et la liberté intérieure</h2>",
         "<p>Le détachement ne signifie pas l'indifférence, mais la capacité à aimer sans posséder. En relâchant l'agrippement aux résultats, le pratiquant découvre une paix stable, indépendante des circonstances extérieures.</p>"),
        ("<h2>À retenir</h2>",
         "<p>La philosophie bouddhiste n'est pas un système abstrait : elle offre des outils concrets — karma, compassion, détachement — pour transformer sa relation au monde et cultiver une sérénité durable.</p>"),
    ],
    "culture": [
        ("<h2>Les symboles sacrés du bouddhisme</h2>",
         "<p>La roue du Dharma, le lotus, la stupa ou encore la statue du Bouddha ne sont pas de simples décorations : chacun véhicule un enseignement précis sur la nature de l'esprit et le chemin de l'éveil.</p>"),
        ("<h2>Les temples et monastères d'Asie</h2>",
         "<p>Du temple de Bodh-Gaya — lieu de l'éveil de Siddhartha — aux monastères du Tibet et de Thaïlande, ces espaces de pratique incarment la transmission vivante d'une tradition millénaire.</p>"),
        ("<h2>Festivals et traditions ancestrales</h2>",
         "<p>Les festivals tels que Vesak (naissance, éveil et parinirvana du Bouddha) rassemblent les communautés autour du chant, de la méditation et de la générosité, perpétuant un héritage partagé.</p>"),
        ("<h2>Vivre la culture au quotidien</h2>",
         "<p>Intégrer un symbole, une récitation ou un rituel léger dans sa journée suffit à relier son existence à une sagesse millénaire, sans rupture avec la vie moderne.</p>"),
    ],
    "comparatifs": [
        ("<h2>Comment choisir son objet spirituel</h2>",
         "<p>Pierres naturelles, mala, statuettes ou encens : chaque objet porte une intention. Notre démarche de comparaison privilégie la transparence des matériaux, l'éthique de sourcing et la cohérence avec votre pratique.</p>"),
        ("<h2>Critères de qualité que nous évaluons</h2>",
         "<ul><li>Origine et authenticité des matériaux</li><li>Durabilité et finition</li><li>Respect des traditions de fabrication</li><li>Rapport qualité-prix honnête</li></ul>"),
        ("<h2>Guides d'achat indépendants</h2>",
         "<p>Nos comparatifs sont rédigés sans pression commerciale. Les liens d'affiliation, lorsqu'ils existent, ne modifient jamais nos recommandations : votre pratique spirituelle reste la priorité.</p>"),
        ("<h2>Notre démarche éditoriale</h2>",
         "<p>Chaque comparatif nait d'une question réelle de pratiquant. Nous testons, sourcons et mettons à jour nos guides pour qu'ils restent utiles années après leur publication.</p>"),
    ],
    "guides": [
        ("<h2>Méditation pour débutants</h2>",
         "<p>Installez-vous confortablement, ramenez l'attention sur la respiration, et laissez les pensées passer sans les saisir. Quinze minutes quotidiennes suffisent pour amorcer un changement durable.</p>"),
        ("<h2>Intégrer la pleine conscience au quotidien</h2>",
         "<p>La pleine conscience ne se limite pas au coussin de méditation : elle consiste à être pleinement présent en marchant, en mangeant, en écoutant. La régularité compte plus que la durée.</p>"),
        ("<h2>Ressources pour approfondir</h2>",
         "<p>Explorez nos articles sur le bouddhisme, les mantras et la respiration pour nourrir votre pratique étape après étape.</p>"),
    ],
    "contact": [
        ("<h2>Nous joindre</h2>",
         "<p>Une question sur une pratique, un article ou un objet ? Notre équipe répond avec bienveillance. Écrivez-nous et nous revenons vers vous dans les meilleurs délais.</p>"),
        ("<h2>Horaires et présence</h2>",
         "<p>Nous accompagnons la communauté en ligne en priorité, pour une accessibilité sans frontière ni attente.</p>"),
    ],
    "formations": [
        ("<h2>Apprendre pas à pas</h2>",
         "<p>La voie bouddhiste se découvre par la pratique régulière plutôt que par l'accumulation théorique. Nos ressources gratuites accompagnent chacun à son rythme.</p>"),
        ("<h2>Structurer sa pratique</h2>",
         "<ul><li>Ancrer un rituel matinal</li><li>Étudier un texte par semaine</li><li>Rejoindre une communauté locale</li><li>Approfondir via la récitation de mantras</li></ul>"),
        ("<h2>Un chemin à vie</h2>",
         "<p>Le bouddhisme ne se « termine » pas : il se rafinne. Acceptez les périodes de moindre ferveur comme faisant partie du parcours, et revisitiez vos ressources quand le besoin se fait sentir.</p>"),
    ],
    "comparatif-bracelets": [
        ("<h2>Bracelets mala : quel matériau choisir ?</h2>",
         "<p>Bois de santal, pierre de lune, améthyste ou rudraksha : chaque matériau soutient une intention différente (calme, clarté, protection). Privilégiez la pierre qui résonne avec votre pratique.</p>"),
        ("<h2>Entretien et intention</h2>",
         "<p>Purifiez votre mala régulièrement (encens, lumière lunaire) et consacrez-le à une intention précise lors de votre première récitation.</p>"),
    ],
    "a-propos": [
        ("<h2>Notre mission</h2>",
         "<p>Bouddhas.fr est un média indépendant dédié au bouddhisme, à la méditation et à la croissance spirituelle. Nous partageons des enseignements accessibles, sourcés et libres de tout dogme.</p>"),
        ("<h2>Nos valeurs</h2>",
         "<ul><li>Autonomie de la pratique</li><li>Respect des traditions</li><li>Contenu gratuit et ouvert</li><li>Bienveillance envers chaque lecteur</li></ul>"),
    ],
}

for slug, sections in ENRICH.items():
    f = ROOT/f"{slug}.html"
    if not f.exists():
        print(f"  ⚠️ {slug}.html introuvable, skip"); continue
    html = f.read_text(encoding="utf-8")
    # Trouver le point d'insertion: avant </article> ou avant le footer/</body>
    added = 0
    for h2, para in sections:
        if h2 in html:
            continue  # déjà présent
        block = f"\n{h2}\n{para}\n"
        # Insérer avant </article> si présent, sinon avant <footer
        if "</article>" in html:
            html = html.replace("</article>", block + "</article>", 1)
        elif "<footer" in html:
            html = html.replace("<footer", block + "<footer", 1)
        else:
            html = html.replace("</body>", block + "</body>", 1)
        added += 1
    f.write_text(html, encoding="utf-8")
    print(f"  ✅ {slug}: +{added} section(s) H2")
print("Enrichissement terminé.")
