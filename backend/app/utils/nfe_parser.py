import xml.etree.ElementTree as ET
import base64
from decimal import Decimal

class NFeParser:
    """Parser para extrair dados de NF-e (XML)"""
    
    # Namespaces comuns em NF-e
    NAMESPACES = {
        'nfe': 'http://www.portalfiscal.inf.br/nfe',
    }
    
    @staticmethod
    def parse_nfe_xml(xml_content):
        """Parse do arquivo XML da NF-e
        
        Retorna um dicionário com as informações extraídas
        """
        try:
            # Se xml_content for string em base64, decodifica
            if isinstance(xml_content, str) and xml_content.startswith('PK'):
                # É um arquivo assinado, tenta extrair o XML
                xml_content = NFeParser._extract_xml_from_signed(xml_content)
            
            # Parse do XML
            root = ET.fromstring(xml_content if isinstance(xml_content, bytes) else xml_content.encode())
            
            # Extrair informações principais
            nfe_info = NFeParser._extract_nfe_info(root)
            supplier_info = NFeParser._extract_supplier_info(root)
            items = NFeParser._extract_items(root)
            
            return {
                'success': True,
                'nfe_info': nfe_info,
                'supplier': supplier_info,
                'items': items
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def _extract_xml_from_signed(signed_content):
        """Extrai XML de um arquivo de NF-e assinado"""
        try:
            # Procura pela tag XML dentro do conteúdo
            start = signed_content.find('<?xml')
            end = signed_content.find('</NFe>') + len('</NFe>')
            if start != -1 and end > start:
                return signed_content[start:end]
        except:
            pass
        return signed_content
    
    @staticmethod
    def _extract_nfe_info(root):
        """Extrai informações da NF-e"""
        try:
            # Procura pelas tags de ide (identificação)
            ide = root.find('.//ide')
            if ide is None:
                ide = root.find('.//{http://www.portalfiscal.inf.br/nfe}ide')
            
            nf_number = ide.findtext('nNF') if ide else None
            nf_series = ide.findtext('serie') if ide else None
            nf_key = root.findtext('.//infNFe/@Id') if root else None
            
            # Extrai datas e valores
            dhEmi = ide.findtext('dhEmi') if ide else None
            dhSaiEnt = ide.findtext('dhSaiEnt') if ide else None
            
            # Valores
            total = root.find('.//total')
            if total is None:
                total = root.find('.//{http://www.portalfiscal.inf.br/nfe}total')
            
            total_amount = Decimal(total.findtext('ICMSTot/vNF') or '0') if total else Decimal('0')
            
            return {
                'nf_number': nf_number,
                'nf_series': nf_series,
                'nf_key': nf_key,
                'emission_date': dhEmi,
                'total_amount': float(total_amount),
            }
        except:
            return {}
    
    @staticmethod
    def _extract_supplier_info(root):
        """Extrai informações do fornecedor/emitente"""
        try:
            emit = root.find('.//emit')
            if emit is None:
                emit = root.find('.//{http://www.portalfiscal.inf.br/nfe}emit')
            
            if emit is None:
                return {}
            
            # CNPJ ou CPF
            cnpj = emit.findtext('CNPJ')
            cpf = emit.findtext('CPF')
            
            # Razão social
            xNome = emit.findtext('xNome')
            
            # Endereço
            enderEmit = emit.find('enderEmit')
            if enderEmit is None:
                enderEmit = emit.find('.//{http://www.portalfiscal.inf.br/nfe}enderEmit')
            
            return {
                'cnpj': cnpj or cpf,
                'name': xNome,
                'street': enderEmit.findtext('xLgr') if enderEmit else None,
                'number': enderEmit.findtext('nro') if enderEmit else None,
                'city': enderEmit.findtext('xMun') if enderEmit else None,
                'state': enderEmit.findtext('UF') if enderEmit else None,
            }
        except:
            return {}
    
    @staticmethod
    def _extract_items(root):
        """Extrai itens da NF-e"""
        items = []
        try:
            # Encontra todos os detalhes de produtos
            details = root.findall('.//det')
            if not details:
                details = root.findall('.//{http://www.portalfiscal.inf.br/nfe}det')
            
            for det in details:
                item_info = NFeParser._parse_item(det)
                if item_info:
                    items.append(item_info)
            
            return items
        except:
            return []
    
    @staticmethod
    def _parse_item(det):
        """Parse de um item individual"""
        try:
            # Produto
            prod = det.find('.//prod')
            if prod is None:
                prod = det.find('.//{http://www.portalfiscal.inf.br/nfe}prod')
            
            if prod is None:
                return None
            
            # Informações básicas
            sku = prod.findtext('cProd')
            description = prod.findtext('xProd')
            quantity = Decimal(prod.findtext('qCom') or '0')
            unit = prod.findtext('uCom')
            unit_price = Decimal(prod.findtext('vUnCom') or '0')
            total_price = Decimal(prod.findtext('vItem') or '0')
            
            # Impostos
            imposto = det.find('.//imposto')
            if imposto is None:
                imposto = det.find('.//{http://www.portalfiscal.inf.br/nfe}imposto')
            
            icms_rate = Decimal('0')
            ipi_rate = Decimal('0')
            pis_rate = Decimal('0')
            cofins_rate = Decimal('0')
            
            if imposto is not None:
                # ICMS
                icms = imposto.find('.//ICMS')
                if icms is None:
                    icms = imposto.find('.//{http://www.portalfiscal.inf.br/nfe}ICMS')
                if icms is not None:
                    # Tenta diferentes grupos de ICMS
                    for icms_group in ['ICMS00', 'ICMS20', 'ICMSST', 'ICMSSN101']:
                        icms_item = icms.find(f'.//{icms_group}')
                        if icms_item is not None:
                            icms_rate = Decimal(icms_item.findtext('pICMS') or '0')
                            break
                
                # IPI
                ipi = imposto.find('.//IPI')
                if ipi is None:
                    ipi = imposto.find('.//{http://www.portalfiscal.inf.br/nfe}IPI')
                if ipi is not None:
                    ipi_item = ipi.find('.//{http://www.portalfiscal.inf.br/nfe}IPITrib')
                    if ipi_item is None:
                        ipi_item = ipi.find('.//IPITrib')
                    if ipi_item is not None:
                        ipi_rate = Decimal(ipi_item.findtext('pIPI') or '0')
            
            return {
                'sku': sku,
                'description': description,
                'quantity': float(quantity),
                'unit': unit,
                'unit_cost': float(unit_price),
                'total_cost': float(total_price),
                'icms_rate': float(icms_rate),
                'ipi_rate': float(ipi_rate),
                'pis_rate': float(pis_rate),
                'cofins_rate': float(cofins_rate),
            }
        except Exception as e:
            print(f"Erro ao processar item: {e}")
            return None
