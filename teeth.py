from maya import cmds

# create ball_CRV and GRP
cmds.circle(nr=(0, 0, 1), c=(0, 0, 0), n='A')
cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), n='B')
cmds.circle(nr=(1, 0, 0), c=(0, 0, 0), n='C')
crvGrp = cmds.group(em=True, name='ball_CRV')
crvShape = ['AShape', 'BShape', 'CShape']
cmds.parent(crvShape, crvGrp, s=1,r=1)
cmds.delete('A', 'B', 'C')
cmds.group(em=True, name='ball_GRP')
cmds.parent('ball_CRV', 'ball_GRP')

# create circle_CRV and GRP
cmds.circle(nr=(0, 0, 1), c=(0, 0, 0), n='circle_CRV')
cmds.group(em=True, name='circle_GRP')
cmds.parent('circle_CRV', 'circle_GRP')

teeth_mst_JNTs = cmds.ls('teeth_*_JNT')
teeth_JNTs = cmds.ls('*_teeth_*_JNT')

cmds.group(em=True, name='teeth_GRP')
cmds.group(em=True, name='teeth_up_CTRL_GRP')
cmds.group(em=True, name='teeth_bot_CTRL_GRP')

# create smaller CTRLs using the ball_CRV
for i in teeth_JNTs:
    grp, ctrl = cmds.duplicate('ball_GRP', n=i.replace('_JNT', '_GRP'), rc=1)
    ctrl = cmds.rename(ctrl, i.replace('_JNT', '_CTRL'))

    cmds.delete(cmds.parentConstraint(i ,grp, mo=0))

    cmds.pointConstraint(ctrl, i)
    cmds.orientConstraint(ctrl, i)
    cmds.scaleConstraint(ctrl, i)

# create mst_CTRLs using circle_CRV
for i in teeth_mst_JNTs:
    grp, ctrl = cmds.duplicate('circle_GRP', n=i.replace('_JNT', '_GRP'), rc=1)
    ctrl = cmds.rename(ctrl, i.replace('_JNT', '_CTRL'))

    cmds.delete(cmds.parentConstraint(i ,grp, mo=0))
    
    cmds.pointConstraint(ctrl, i)
    cmds.orientConstraint(ctrl, i)
    cmds.scaleConstraint(ctrl, i)

# tidy up the scene
teeth_up_CTRL = cmds.ls('*_teeth_up_*_*_GRP')
teeth_bot_CTRL = cmds.ls('*_teeth_bot_*_*_GRP')
cmds.parent(teeth_up_CTRL, 'teeth_up_CTRL_GRP')
cmds.parent(teeth_bot_CTRL, 'teeth_bot_CTRL_GRP')
cmds.parent('teeth_up_CTRL_GRP', 'teeth_up_CTRL')
cmds.parent('teeth_bot_CTRL_GRP', 'teeth_bot_CTRL')

cmds.delete('ball_GRP')
cmds.delete('circle_GRP')
