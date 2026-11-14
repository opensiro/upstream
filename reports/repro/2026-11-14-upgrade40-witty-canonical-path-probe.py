"""Source-native WittyCode symlink consent-card path falsifier on Python 3.11.
Windows-only security assertions are excluded: this runs on Linux, not the target OS.
"""
from pathlib import Path
import tempfile,sys,os,json,hashlib
root=Path(os.environ.get("OPENSIRO_BATCH40_ROOT", Path.cwd())).resolve()
source=root/'sources/WittyRyuji__WittyCode'
sys.path[:0]=[str(source)]
from desktop.core.harness.permissions import action_view, decide
from desktop.core.harness.fs_tools import EDIT_FILE
from desktop.core.harness.tools import ToolContext
with tempfile.TemporaryDirectory(prefix='witty-b40-') as td:
    temp=Path(td);project=temp/'project';project.mkdir();inside=project/'inside.txt';inside.write_text('prior\n')
    outside=temp/'outside';outside.mkdir();target=outside/'external.txt';target.write_text('prior\n')
    (project/'alias-in.txt').symlink_to(inside)
    (project/'alias-out.txt').symlink_to(target)
    ctx=ToolContext(project=project)
    rows=[]
    for alias,actual in [('alias-in.txt',inside),('alias-out.txt',target)]:
        args={'file_path':alias,'old_str':'prior','new_str':'changed'}
        view=action_view('research-b40',EDIT_FILE,args,ctx)
        decision=decide('code',EDIT_FILE,args,ctx,remembered=set())
        assert view.path==str(actual.resolve()),(alias,view.path,actual)
        assert len(view.diffs)==1
        rows.append({'alias':alias,'expected_canonical_path':str(actual.resolve()),'view_path':view.path,'decision':decision.verdict,'ui_title':view.title})
    assert rows[1]['decision']!='allow',rows[1]
record={'name':'wittycode-canonical-symlink-approval-view','source':'WittyRyuji/WittyCode','pin':'555b3c060de633c4cd98b21ba56c84d7487be527','python':'3.11.18','platform':'linux','result':'PASS: approval-card action_view resolves both inside and outside symlink target paths, and outside edit is not auto-allowed','cases':rows,'limitation':'Only portable fs_tools path and approval-card code on Linux; not a GUI browser or Windows junction test; does not prove platform-specific UI rendering.'}
(root/'receipts/wittycode-canonical-symlink-approval-view.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
