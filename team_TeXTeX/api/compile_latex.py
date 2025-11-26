from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

import subprocess
import os
import shutil

@require_http_methods(["POST"])
@csrf_exempt
def compile_latex(request):
    """
    POSTリクエストを受け取り、LaTeXコードをコンパイルしてPDFを生成します。
    """
    latex_code = request.POST.get('latex_code', '')

    # 一時ファイルのディレクトリ設定
    TEMP_DIR = os.path.join(settings.BASE_DIR, 'temp_latex')
    os.makedirs(TEMP_DIR, exist_ok=True)

    TEX_FILENAME = 'document.tex'
    PDF_FILENAME = 'document.pdf'
    TEX_PATH = os.path.join(TEMP_DIR, TEX_FILENAME)
    
    try:
        # 1. LaTeXコードをファイルに書き込み
        with open(TEX_PATH, 'w', encoding='utf-8') as f:
            f.write(latex_code)

        # 2. lualatexでコンパイル実行
        result = subprocess.run(
            ['lualatex', '-interaction=nonstopmode', f'-output-directory={TEMP_DIR}', TEX_FILENAME],
            cwd=TEMP_DIR,
            capture_output=True,
            text=True,
            check=False 
        )
        
        # 3. コンパイル結果の確認とPDFの読み込み
        PDF_PATH = os.path.join(TEMP_DIR, PDF_FILENAME)
        
        if os.path.exists(PDF_PATH):
            with open(PDF_PATH, 'rb') as f:
                pdf_data = f.read()
            
            import base64
            pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')

            log_content = result.stdout + result.stderr

            return JsonResponse({
                'status': 'success',
                'pdf_base64': pdf_base64,
                'log': log_content,
            })
        else:
            log_content = result.stdout + result.stderr
            return JsonResponse({
                'status': 'error',
                'message': 'PDFの生成に失敗しました。LaTeXコードを確認してください。',
                'log': log_content,
            })

    except FileNotFoundError:
        return JsonResponse({
            'status': 'error',
            'message': 'コンパイラ (lualatex) が見つかりませんでした。環境設定を確認してください。',
            'log': 'Compiler not found.',
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'予期せぬエラーが発生しました: {str(e)}',
            'log': str(e),
        })
    finally:
        # 4. 一時ファイルのクリーンアップ
        try:
            shutil.rmtree(TEMP_DIR)
        except OSError as e:
            print(f"Error: Directory cleanup failed: {e.strerror}")