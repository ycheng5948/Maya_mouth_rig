from maya import cmds

# create and name CTRLs and orient the GRP correctly
#creating ball ctrl
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

all_JNT = cmds.listRelatives('tongue_0_JNT', ad=1) + ['tongue_0_JNT']

side_GRP = []
end_GRP = []

for i in all_JNT:
    if len(i.split('_'))==3:
        m_grp, ctrl = cmds.duplicate('circle_GRP', n=i.replace('_JNT', '_GRP'), rc=1)
        ctrl = cmds.rename(ctrl, i.replace('_JNT', '_CTRL'))

        cmds.delete(cmds.parentConstraint(i ,m_grp, mo=0))
        cmds.pointConstraint(ctrl, i)
        cmds.orientConstraint(ctrl, i)
        cmds.scaleConstraint(ctrl, i)

    elif len(i.split('_'))==4:
        t_grp, ctrl = cmds.duplicate('ball_GRP', n=i.replace('_JNT', '_GRP'), rc=1)
        ctrl = cmds.rename(ctrl, i.replace('_JNT', '_CTRL'))

        cmds.delete(cmds.parentConstraint(i ,t_grp, mo=0))
        cmds.pointConstraint(ctrl, i)
        cmds.orientConstraint(ctrl, i)
        cmds.scaleConstraint(ctrl, i)

        side_GRP.append(t_grp)

    elif '_end' in i:
        e_grp, ctrl = cmds.duplicate('ball_GRP', n=i.replace('_JNT', '_GRP'), rc=1)
        ctrl = cmds.rename(ctrl, i.replace('_JNT', '_CTRL'))

        cmds.delete(cmds.parentConstraint(i ,e_grp, mo=0))
        cmds.pointConstraint(ctrl, i)
        cmds.orientConstraint(ctrl, i)
        cmds.scaleConstraint(ctrl, i)

        end_GRP.append(e_grp)

for i in side_GRP:
    cmds.parent(i, i[2:])
for i in end_GRP:
    cmds.parent(i, i.replace('_end_GRP', '_CTRL'))

cmds.delete('ball_GRP')
cmds.delete('circle_GRP')
