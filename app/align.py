import copy
import glob
import json
import traceback

import collatex

import lxml.etree as ET


# L'ordre es différents alignements est manuel. Voyons un cas précis
# Dans Z on a toute la partie 3. C'est sur quoi on va travailler.

def test_file_writing(object, name, format):
    with open(f"/home/mgl/Documents/{name}", "w") as output_file:
        if format == "json":
            json.dump(object, output_file)


class Aligner:
    def __init__(self, filePath: str, main_file: str):
        # On parse chaque fichier
        self.tei_ns = 'http://www.tei-c.org/ns/1.0'
        self.ns_decl = {'tei': self.tei_ns}
        self.main_file = ET.parse(main_file)
        target_files = glob.glob(filePath)
        self.dict_of_parsed_files = {}
        for file in target_files:
            self.dict_of_parsed_files[file.split("/")[-1].replace(".xml", "")] = ET.parse(file)

        # On crée les arbres de sortie à partir des arbres d'entrée
        self.output_tree = {key: copy.deepcopy(tree) for key, tree in self.dict_of_parsed_files.items()}

        self.target_tokens, self.target_ids, self.tokens_and_ids = dict(), dict(), dict()

        print("Retrieving tokens for each document")
        for basename, target_file in self.dict_of_parsed_files.items():
            print(basename)
            self.target_tokens[basename] = target_file.xpath("descendant::node()[self::tei:w or self::tei:pc]/@lemma",
                                                             namespaces=self.ns_decl)
            self.target_ids[basename] = target_file.xpath("descendant::node()[self::tei:w or self::tei:pc]/@xml:id",
                                                          namespaces=self.ns_decl)
            self.tokens_and_ids[basename] = list(zip(self.target_tokens[basename], self.target_ids[basename]))

        self.words_and_pc = dict()
        for basename, target_file in self.output_tree.items():
            self.words_and_pc[basename] = target_file.xpath("descendant::node()[self::tei:pc or self::tei:w]",
                                                            namespaces=self.ns_decl)

        self.all_nodes = dict()
        for basename, target_file in self.output_tree.items():
            self.all_nodes[basename] = target_file.xpath("descendant::tei:div[@type='partie']/descendant::node()",
                                                         namespaces=self.ns_decl)

    def structure_tree(self, elements: list, tokens:list, indices: list, context, index_context, query):
        print(indices)
        context_target_nodes = self.output_tree["Mad_A"].xpath(context, namespaces=self.ns_decl)[index_context]
        for index, (min_range, max_range) in enumerate(indices):
            element = elements[index]
            element_name = element.xpath("name()")
            # On récupère les attributs sous la forme d'un dictionnaire
            attributes = element.attrib
            print(element_name)
            # Va savoir pourquoi mais l'argument nsmap ne fonctionne pas ici.
            element_to_insert = ET.Element("{" + self.tei_ns + "}" + element_name)
            for attribute, value in attributes.items():
                element_to_insert.set(attribute, value)
            try:

                # Pour l'instant c'est fait pour fonctionner par appui successif sur la division antérieure, ce qui
                # ne fonctionne pas dans le cas où on n'en place qu'une. Modifier cela.
                current_index = min_range
                print(current_index)
                preceding_anchor = tokens[current_index]
            except IndexError:
                print("Index error")
            print(current_index)
            # On fonctionne différemment pour le premier élément de la liste
            if index != 0:
                print("Placing anchor after element")
                preceding_anchor.addnext(element_to_insert)
            else:
                print("Placing anchor before element")
                print(len(tokens))
                following_anchor = tokens[max_range]
                following_anchor.addprevious(element_to_insert)
            [self.write_tree(f"/home/mgl/Documents/test/{basename}_{element_name}_intermed.xml", self.output_tree[basename])
             for basename in self.output_tree.keys()]

        print("Starting transformation")
        # On va tout calculer une fois plutôt que de le faire à chaque mot ou à chaque paragraphe.
        # On crée une liste qui contient les W et P, qu'on va transformer en dictionnaire avec comme clé
        # l'identifiant du tei:p et comme valeur la liste des objets tei:w
        # À partir de là, on itère sur les tei:p vides pour y mettre les noeuds enfants tei:w
        print(query)
        all_divs = context_target_nodes.xpath(query, namespaces=self.ns_decl)
        all_nodes = context_target_nodes.xpath(f"descendant::node()[not(self::text())]", namespaces=self.ns_decl)
        all_ids = context_target_nodes.xpath(
            f"descendant::node()[not(self::text())]/@*[name()='n' or name()='xml:id']", namespaces=self.ns_decl)
        elements_and_ids = list(zip(all_nodes, all_ids))
        p_dict = {}
        element_name = all_divs[0].xpath("name()")

        current_div = all_divs[0].xpath("@n")[0]
        if len(all_divs) == 1:
            elements_and_ids = elements_and_ids[min_range: max_range + 1]
        for element, identifier in elements_and_ids:
            if element.xpath("name()") != element_name:
                try:
                    p_dict[current_div].append(element)
                except KeyError:
                    p_dict[current_div] = [element]
            else:
                current_div = element.xpath("@n")[0]


        # On insère les tei:w dans le paragraphe correspondant de la div correspondante
        print(p_dict.keys())
        for div in all_divs:
            div_n = div.xpath("@n")[0]
            # Gestion de la première division
            try:
                print("Test")
                print(len(p_dict[div_n]))
                for word in p_dict[div_n]:
                    div.append(word)
            except KeyError:
                continue
        # On supprime les éléments sans parent p:
        # https://stackoverflow.com/a/7981894
        # for orphan_node in self.output_tree[key].xpath("descendant::tei:div[@type='partie']/descendant::node()[not("
        #                                                "ancestor::tei:div[@type='chapitre'])]",
        #                                                namespaces=self.ns_decl):
        #     orphan_node.getparent().remove(orphan_node)
        #     print("Removing orphan")
        print("Done !")

    def write_tree(self, path, tree):
        print(f"Writing file to {path}")
        with open(path, "w") as output_file:
            output_file.write(ET.tostring(tree, pretty_print=True).decode('utf8'))

    def get_chapter_positions(self):
        chaps_main = self.main_file.xpath("//tei:div[@type='chapitre']", namespaces=self.ns_decl)
        chaps_target = self.dict_of_parsed_files["Mad_A"].xpath("//tei:div[@type='chapitre']", namespaces=self.ns_decl)
        indices_main = []
        indices_target = []
        for chapter in chaps_main:
            indices_main.append(len(chapter.xpath(
                f"descendant::node()[self::tei:w or self::tei:pc][1]/preceding::node()[self::tei:w or self::tei:pc]",
                namespaces=self.ns_decl)))

        for chapter in chaps_target:
            indices_target.append(len(chapter.xpath(
                f"descendant::node()[self::tei:w or self::tei:pc][1]/preceding::node()[self::tei:w or self::tei:pc]",
                namespaces=self.ns_decl)))
        diffs_main = []
        for index, value in enumerate(indices_main[1:]):
            diffs_main.append(value - indices_main[index])

        diffs_target = []
        for index, value in enumerate(indices_target[1:]):
            diffs_target.append(value - indices_target[index])
        print(indices_main)
        print(diffs_main)
        print(indices_target)
        print(diffs_target)

    def print_aligned_sents(self, aligned_table: list, index):
        try:
            wit_a_sent = " ".join([wit_a['t'] if wit_a else "" for wit_a, _ in aligned_table[index - 10:index + 10]])
            wit_a_sent = wit_a_sent.replace(" .", ".").replace(" ,", ",")
            wit_b_sent = " ".join([wit_b['t'] if wit_b else "" for wit_a, wit_b in aligned_table[index - 10:index + 10]])
            wit_b_sent = wit_b_sent.replace(" .", ".").replace(" ,", ",")
            print("Aligned sentences:")
            print(f"{wit_a_sent}\n{wit_b_sent}")
        except Exception:
            print(traceback.format_exc())

    def check_if_match(self, json_table: str, target_id: str) -> (bool, str):
        json_table = json.loads(json_table)
        aligned_table = list(zip([token[0] if token else None for token in json_table['table'][0]],
                                 [token[0] if token else None for token in json_table['table'][1]]))
        test_file_writing(object=aligned_table, name="aligned.json", format="json")
        print(target_id)
        for index, (base_witness, witness_b) in enumerate(aligned_table):
            if base_witness and witness_b:
                if base_witness['xml:id'] == target_id:
                    print("Found target")
                    print(base_witness)
                    print(witness_b)
                    if base_witness['t'] == witness_b['t']:
                        self.print_aligned_sents(aligned_table=aligned_table, index=index)
                        return True, witness_b['xml:id']

    def align(self, query, context, proportion):
        print(f"Trying to align on {query} with {context} context.")
        # On veut d'abord aligner les chapitres
        # Puis les titres de chapitre
        # Puis les divisions.
        # On a donc besoin d'une fonction d'alignement avec un XPATH.
        # Première requête: "//tei:div[@type='chapitre']"
        # On va itérer sur chaque division
        # On prend le nombre de mots de la division source,
        # et on va chercher dans cette zone à aligner la source et la cible
        # Pour la première division c'est facile
        # Pour la suite, il faut mettre à jour la zone en fonction de la longueur de la division de la cible
        # Point faible de cette méthode: ça fonctionne de manière incrémentielle,
        # et si ça bloque quelque part, le processus complet est bloqué.
        # Il faudra probablement recourir à une méthode de text reuse en complément.
        # TODO: Bien penser à passer à des boucles pour gérer + de deux textes.
        context_source_nodes = self.main_file.xpath(context, namespaces=self.ns_decl)
        context_target_nodes = self.output_tree["Mad_A"].xpath(context, namespaces=self.ns_decl)
        for index_context, (context_source_node, context_target_node) in enumerate(list(zip(context_source_nodes, context_target_nodes))):
            structure_source_elements = context_source_node.xpath(query, namespaces=self.ns_decl)
            target_tokens = context_target_node.xpath("descendant::node()[self::tei:w or self::tei:pc]",
                                                 namespaces=self.ns_decl)
            target_lemmas = context_target_node.xpath("descendant::node()[self::tei:w or self::tei:pc]/@lemma",
                                                 namespaces=self.ns_decl)
            target_ids = context_target_node.xpath("descendant::node()[self::tei:w or self::tei:pc]/@xml:id",
                                             namespaces=self.ns_decl)
            target_tokens_ids = list(zip(target_tokens, target_ids))
            current_source_position = 0
            current_target_position = 0
            source_tokens = context_source_node.xpath("descendant::node()[self::tei:w or self::tei:pc]/@lemma",
                                                 namespaces=self.ns_decl)
            source_ids = context_source_node.xpath("descendant::node()[self::tei:w or self::tei:pc]/@xml:id",
                                             namespaces=self.ns_decl)
            source_tokens_id = list(zip(source_tokens, source_ids))
            target_positions = [0, ]
            for index, division in enumerate(structure_source_elements):
                first_token_following_div = division.xpath(
                    "descendant::node()[self::tei:w or self::tei:pc][last()]/@xml:id", namespaces=self.ns_decl)[0]
                print(first_token_following_div)
                source_tokens_per_div = division.xpath("descendant::node()[self::tei:w or self::tei:pc]/@lemma",
                                                       namespaces=self.ns_decl)
                number_of_tokens_in_div = len(source_tokens_per_div)
                tokens_fraction = round(number_of_tokens_in_div * proportion)
                current_source_position += number_of_tokens_in_div
                source_search_range = [current_source_position - tokens_fraction,
                                       current_source_position + tokens_fraction]
                if index == 0:
                    current_target_position = number_of_tokens_in_div
                else:
                    current_target_position += number_of_tokens_in_div
                target_search_range = [current_target_position - tokens_fraction,
                                       current_target_position + tokens_fraction]
                print(current_target_position)
                print(f"Source search range: {source_search_range}")
                print(f"Target search range: {target_search_range}")
                source_tokens_to_compare = source_tokens_id[source_search_range[0]: source_search_range[1]]
                source_list = [{"t": lemma, "xml:id": id} for lemma, id in source_tokens_to_compare]
                collatex_dict = {"witnesses": [{"id": "Sev_Z", "tokens": source_list}]}
                for basename, target_file in self.dict_of_parsed_files.items():
                    zip_target_token_id = list(zip(target_lemmas, target_ids))
                    if index == 0:
                        target_tokens_to_compare = zip_target_token_id[source_search_range[0]: source_search_range[1]]
                    else:
                        target_tokens_to_compare = zip_target_token_id[target_search_range[0]: target_search_range[1]]
                    target_list = [{"t": lemma, "xml:id": id} for lemma, id in target_tokens_to_compare]
                    collatex_dict["witnesses"].append({"id": basename, "tokens": target_list})
                print("Collating")
                collation_table = collatex.collate(collation=collatex_dict, output="json", segmentation=False)
                # print(collation_table)
                try:
                    match, matching_id = self.check_if_match(json_table=collation_table,
                                                             target_id=first_token_following_div)
                    print(f"Div {index + 1} aligned.")
                    print(matching_id)
                    current_target_position = \
                        [index for index, (token, id) in enumerate(target_tokens_ids) if id == matching_id][
                            0]
                    print(f"Current position: {current_target_position}")
                    target_positions.append(current_target_position)

                except TypeError:
                    print(first_token_following_div)
                    print(f"Unable to align div {index + 1}. Exiting.")
                    # collation_table = collatex.collate(collation=collatex_dict, output="csv", segmentation=False)
                    # with open(f"/home/mgl/Documents/tsv_{index + 2}.tsv", "w") as output_file:
                    #     output_file.write(collation_table)
                    break
            print(target_positions)
            target_positions = [(target_positions[index], target_positions[index + 1]) for index, _
                                in enumerate(target_positions[:len(target_positions) - 1])]
            print(target_positions)
            self.structure_tree(elements=structure_source_elements, tokens=target_tokens,
                                indices=target_positions, context=context, index_context=index_context, query=query)
            [self.write_tree(f"/home/mgl/Documents/test/{basename}.xml", self.output_tree[basename])
             for basename in self.output_tree.keys()]


if __name__ == '__main__':
    # La requête à effectuer
    example_query_1 = "//tei:div[@type='chapitre']"
    # Le contexte pour boucler
    context_query_1 = "//tei:div[@type='partie']"

    # La requête à effectuer
    example_query_2 = "//tei:head"
    # Le contexte pour boucler
    context_query_2 = "//tei:div[@type='chapitre']"

    example_query_2 = "descendant::tei:head"
    aligner = Aligner(filePath="/home/mgl/Bureau/Travail/projets/alignement/alignement_global_unilingue/data"
                               "/transform/Mad_A.xml",
                      main_file="/home/mgl/Bureau/Travail/projets/alignement/alignement_global_unilingue/data/Source"
                                "/Sev_Z.xml")
    aligner.align(query=example_query_1, context=context_query_1,
                  proportion=.15)
    # Le titre est plus variable et plus court, il est donc utile d'augmenter la fenêtre de comparaison à 1 voire 2 fois la taille de la division
    aligner.align(query=example_query_2, context=context_query_2, proportion=1)
