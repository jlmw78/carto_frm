"""
Model exported as python.
Name : limitipo
Group : mios
With QGIS : 31608
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterField
from qgis.core import QgsProcessingParameterFeatureSource
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsProcessingParameterBoolean
from qgis.core import QgsProcessingParameterDefinition
import processing


class Limitipo(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        param = QgsProcessingParameterField('campolink', 'campo link', type=QgsProcessingParameterField.Any, parentLayerParameterName='fgh', allowMultiple=False, defaultValue='link')
        param.setFlags(param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(param)
        self.addParameter(QgsProcessingParameterFeatureSource('fgh', 'poligonos', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Limites_radios', 'limites_radios', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(17, model_feedback)
        results = {}
        outputs = {}

        # Multiparte a monoparte
        alg_params = {
            'INPUT': parameters['fgh'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MultiparteAMonoparte'] = processing.run('native:multiparttosingleparts', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # POligonos a lineas
        alg_params = {
            'INPUT': outputs['MultiparteAMonoparte']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PoligonosALineas'] = processing.run('native:polygonstolines', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # v.clean
        alg_params = {
            '-b': False,
            '-c': False,
            'GRASS_MIN_AREA_PARAMETER': 0.0001,
            'GRASS_OUTPUT_TYPE_PARAMETER': 0,
            'GRASS_REGION_PARAMETER': None,
            'GRASS_SNAP_TOLERANCE_PARAMETER': -1,
            'GRASS_VECTOR_DSCO': '',
            'GRASS_VECTOR_EXPORT_NOCAT': False,
            'GRASS_VECTOR_LCO': '',
            'input': outputs['PoligonosALineas']['OUTPUT'],
            'threshold': '',
            'tool': [0,1,2,3,4,5,6,7,8,9,10,11,12],
            'type': [0,1,2,3,4,5,6],
            'error': QgsProcessing.TEMPORARY_OUTPUT,
            'output': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Vclean'] = processing.run('grass7:v.clean', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Diferencia
        alg_params = {
            'INPUT': outputs['PoligonosALineas']['OUTPUT'],
            'OVERLAY': outputs['Vclean']['error'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Diferencia'] = processing.run('native:difference', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Unir capas vectoriales
        alg_params = {
            'CRS': 'ProjectCrs',
            'LAYERS': [outputs['Diferencia']['OUTPUT'],outputs['Vclean']['error']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['UnirCapasVectoriales'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Rehacer campos
        alg_params = {
            'FIELDS_MAPPING': [{'expression': '$id+1','length': 0,'name': 'fid','precision': 0,'type': 4}],
            'INPUT': outputs['UnirCapasVectoriales']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RehacerCampos'] = processing.run('qgis:refactorfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Buffer_der
        alg_params = {
            'DISTANCE': 1,
            'INPUT': outputs['RehacerCampos']['OUTPUT'],
            'JOIN_STYLE': 1,
            'MITER_LIMIT': 2,
            'SEGMENTS': 8,
            'SIDE': 1,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Buffer_der'] = processing.run('qgis:singlesidedbuffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Punto_der
        alg_params = {
            'ALL_PARTS': True,
            'INPUT': outputs['Buffer_der']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Punto_der'] = processing.run('native:pointonsurface', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Buffer_izq
        alg_params = {
            'DISTANCE': 1,
            'INPUT': outputs['RehacerCampos']['OUTPUT'],
            'JOIN_STYLE': 1,
            'MITER_LIMIT': 2,
            'SEGMENTS': 8,
            'SIDE': 0,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Buffer_izq'] = processing.run('qgis:singlesidedbuffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Unir_der
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['Punto_der']['OUTPUT'],
            'JOIN': parameters['fgh'],
            'JOIN_FIELDS': parameters['campolink'],
            'METHOD': 1,
            'PREDICATE': [0],
            'PREFIX': 'der_',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Unir_der'] = processing.run('qgis:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Punto_izq
        alg_params = {
            'ALL_PARTS': True,
            'INPUT': outputs['Buffer_izq']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Punto_izq'] = processing.run('native:pointonsurface', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # campos_der
        alg_params = {
            'FIELDS_MAPPING': [{'expression': '\"fid\"','length': 0,'name': 'fid','precision': 0,'type': 4},{'expression': ' substr( \"der_link\",0,2)','length': 2,'name': 'der_p','precision': 0,'type': 10},{'expression': ' substr( \"der_link\",0,5)','length': 5,'name': 'der_pd','precision': 0,'type': 10},{'expression': ' substr( \"der_link\",0,7)','length': 7,'name': 'der_pdf','precision': 0,'type': 10},{'expression': '\"der_link\"','length': 254,'name': 'der_pdfr','precision': 0,'type': 10}],
            'INPUT': outputs['Unir_der']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Campos_der'] = processing.run('qgis:refactorfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # Unir_izq
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['Punto_izq']['OUTPUT'],
            'JOIN': parameters['fgh'],
            'JOIN_FIELDS': parameters['campolink'],
            'METHOD': 1,
            'PREDICATE': [0],
            'PREFIX': 'izq_',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Unir_izq'] = processing.run('qgis:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # campos_izq
        alg_params = {
            'FIELDS_MAPPING': [{'expression': '\"fid\"','length': 0,'name': 'fid','precision': 0,'type': 4},{'expression': ' substr( \"izq_link\",0,2)','length': 2,'name': 'izq_p','precision': 0,'type': 10},{'expression': ' substr( \"izq_link\",0,5)','length': 5,'name': 'izq_pd','precision': 0,'type': 10},{'expression': ' substr( \"izq_link\",0,7)','length': 7,'name': 'izq_pdf','precision': 0,'type': 10},{'expression': '\"izq_link\"','length': 9,'name': 'izq_pdfr','precision': 0,'type': 10}],
            'INPUT': outputs['Unir_izq']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Campos_izq'] = processing.run('qgis:refactorfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # Unir_1
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'fid',
            'FIELDS_TO_COPY': None,
            'FIELD_2': 'fid',
            'INPUT': outputs['RehacerCampos']['OUTPUT'],
            'INPUT_2': outputs['Campos_izq']['OUTPUT'],
            'METHOD': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Unir_1'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        # Unir_2
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'fid',
            'FIELDS_TO_COPY': None,
            'FIELD_2': 'fid',
            'INPUT': outputs['Unir_1']['OUTPUT'],
            'INPUT_2': outputs['Campos_der']['OUTPUT'],
            'METHOD': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Unir_2'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(16)
        if feedback.isCanceled():
            return {}

        # campos_izq_der
        alg_params = {
            'FIELDS_MAPPING': [{'expression': '\"fid\"','length': 0,'name': 'fid','precision': 0,'type': 4},{'expression': '\"izq_p\"','length': 2,'name': 'izq_p','precision': 0,'type': 10},{'expression': '\"izq_pd\"','length': 5,'name': 'izq_pd','precision': 0,'type': 10},{'expression': '\"izq_pdf\"','length': 7,'name': 'izq_pdf','precision': 0,'type': 10},{'expression': '\"izq_pdfr\"','length': 9,'name': 'izq_pdfr','precision': 0,'type': 10},{'expression': '\"der_p\"','length': 2,'name': 'der_p','precision': 0,'type': 10},{'expression': '\"der_pd\"','length': 5,'name': 'der_pd','precision': 0,'type': 10},{'expression': '\"der_pdf\"','length': 7,'name': 'der_pdf','precision': 0,'type': 10},{'expression': '\"der_pdfr\"','length': 9,'name': 'der_pdfr','precision': 0,'type': 10},{'expression': 'case when (\"der_p\"  <> \"izq_p\") then \'prov\' else \ncase when (\"der_pd\" <> \"izq_pd\") then \'dep\' else \ncase when (\"der_pdf\" <> \"izq_pdf\") then \'frac\' else\ncase when (\"der_pdfr\" <> \"izq_pdfr\") then \'rad\' else\n\'VER\' end end end end','length': 10,'name': 'limite','precision': 0,'type': 10}],
            'INPUT': outputs['Unir_2']['OUTPUT'],
            'OUTPUT': parameters['Limites_radios']
        }
        outputs['Campos_izq_der'] = processing.run('qgis:refactorfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Limites_radios'] = outputs['Campos_izq_der']['OUTPUT']
        return results

    def name(self):
        return 'limitipo'

    def displayName(self):
        return 'limitipo'

    def group(self):
        return 'mios'

    def groupId(self):
        return 'mios'

    def shortHelpString(self):
        return """<html><body><h2>Descripción del algoritmo</h2>
<p>Genera, a partir de poligonos de radios, los limites clasificados segun su tipo</p>
<h2>Parámetros de entrada</h2>
<h3>campo link</h3>
<p>campo que contiene concatenado los valores de prov, depto, frac y rad</p>
<h3>poligonos</h3>
<p>capa de poligonos </p>
<h3>limites_radios</h3>
<p>arcos clasificados segun el tipo de limite</p>
<h3>Verbose logging</h3>
<p></p>
<h2>Salidas</h2>
<h3>limites_radios</h3>
<p>arcos clasificados segun el tipo de limite</p>
<br><p align="right">Autor del algoritmo: jlmw78</p><p align="right">Versión del algoritmo: 202106</p></body></html>"""

    def createInstance(self):
        return Limitipo()
