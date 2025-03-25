from maya import cmds

# after the 2 initial CRVs are created from GEO
CRVs = ['lip_top_CRV', 'lip_bot_CRV']
# needed_CRVs = ['lip_top_CRV', 'lip_bot_CRV', 'lip_jaw_top_CRV', 'lip_jaw_bot_CRV']
# needed_JNTs = ['lip_jaw_top_JNT', 'lip_jaw_mid_JNT', 'lip_jaw_bot_JNT']
cmds.delete("lip_top_CRV", ch=True)
cmds.delete("lip_bot_CRV", ch=True)

for i in CRVs:
    cmds.duplicate(i, n=i.replace('lip_', 'lip_jaw_'))

# rebuilding the lip_jaw_CRVs
cmds.rebuildCurve('lip_jaw_top_CRV', ch=1, rpo=1, rt=0, end=1, kr=2, kcp=0, kep=1, kt=0, s=6, d=3, tol=0.01)
cmds.rebuildCurve('lip_jaw_bot_CRV', ch=1, rpo=1, rt=0, end=1, kr=2, kcp=0, kep=1, kt=0, s=6, d=3, tol=0.01)
cmds.delete("lip_jaw_top_CRV", ch=True)
cmds.delete("lip_jaw_bot_CRV", ch=True)

# create and setting up jaw_top/mid/bot_JNTs
jaw_top_jnt = cmds.createNode("joint", n='lip_jaw_top_JNT')
cmds.delete(cmds.parentConstraint(jaw_top_jnt, 'jaw_JNT', mo=False))
jaw_mid_jnt = cmds.duplicate(jaw_top_jnt, n=jaw_top_jnt.replace('top_', 'mid_'))
jaw_bot_jnt = cmds.duplicate(jaw_top_jnt, n=jaw_top_jnt.replace('top_', 'bot_'))

cmds.parentConstraint(jaw_top_jnt, 'jaw_JNT', mo=1)
cmds.parentConstraint(jaw_top_jnt, jaw_bot_jnt, jaw_mid_jnt, mo=1)

# bind jaw_top/mid/bot_JNTs to jaw_CRVs
cmds.skinCluster(jaw_top_jnt, jaw_mid_jnt, 'lip_jaw_top_CRV', dr=4)
cmds.skinCluster(jaw_mid_jnt, jaw_bot_jnt, 'lip_jaw_bot_CRV', dr=4)

# create jaw_CTRL using simple circle and move to jaw_JNT
cmds.circle(nr=(0, 0, 1), c=(0, 0, 0), n='circle_CRV')
cmds.group(em=True, name='circle_GRP')
cmds.parent('circle_CRV', 'circle_GRP')

grp = cmds.duplicate('circle_GRP', name='jaw_GRP', rc=1)[0]
ctrl = cmds.listRelatives(grp, c=True)[0]
ctrl = cmds.rename(ctrl, 'jaw_CTRL')
cmds.delete(cmds.parentConstraint('jaw_GRP', 'jaw_JNT'))
cmds.delete('circle_GRP')
###################################################################
# manually editing jaw_CTRL, placing/shaping to the desired look
###################################################################
# manually editing weight deformer in smooth skin in component editor
###################################################################
# creating crn_CRVs
cmds.duplicate('lip_jaw_top_CRV', n=jaw_top_jnt.replace('_jaw', '_crn'))
cmds.duplicate('lip_jaw_bot_CRV', n=jaw_top_jnt.replace('_jaw', '_crn'))
cmds.delete('lip_crn_top_CRVShapeOrig')
cmds.delete('lip_crn_bot_CRVShapeOrig')

L_lip_crn_jnt = cmds.createNode("joint", n='L_lip_crn_JNT')
M_lip_crn_jnt = cmds.createNode("joint", n='M_lip_crn_JNT')

# identifying the left corner CV
def find_L_crn(crv):
    CVs = cmds.ls(crv + ".cv[*]",fl=True)
    n = len(CVs)
    space_lst = []
    for i in range(0, n+1):
        space = cmds.xform('{0}.cv[{1}]'.format(crv, i), q=1, t=1, ws=1)
        space_lst.append(space)

    if space_lst[0][0] > space_lst[-1][0]:
        print('space0 is left corner')
        lip_crn = cmds.xform('{0}.cv[0]'.format(crv), q=1, t=1, ws=1)
        cmds.move(lip_crn[0], lip_crn[1], lip_crn[2], L_lip_crn_jnt)
        cmds.move(0, lip_crn[1], lip_crn[2], M_lip_crn_jnt)
    else:
        print('space0 is right corner')
        lip_crn = cmds.xform('{0}.cv[{1}]'.format(crv, n), q=1, t=1, ws=1)
        cmds.move(lip_crn[0], lip_crn[1], lip_crn[2], L_lip_crn_jnt)
        cmds.move(0, lip_crn[1], lip_crn[2], M_lip_crn_jnt)

find_L_crn('lip_crn_top_CRV')
###################################################################
# manually orient the joints based on the face's curviture
R_lip_crn_jnt = cmds.mirrorJoint(L_lip_crn_jnt, mirrorYZ=1, mirrorBehavior=1, searchReplace=('L_', 'R_'))
###################################################################
# creating BS from crn_CRVs to jaw_CRVs
cmds.blendShape('lip_crn_top_CRV', 'lip_jaw_top_CRV', n='lip_jaw_top_BS', ex='deformPartition\#')
cmds.blendShape('lip_crn_bot_CRV', 'lip_jaw_bot_CRV', n='lip_jaw_bot_BS', ex='deformPartition\#')
cmds.blendShape('lip_jaw_top_BS', edit=True, w=[0, 1])
cmds.blendShape('lip_jaw_bot_BS', edit=True, w=[0, 1])
###################################################################
# creating 4 mst_CTRLs, left(L), right(R), top(T), and bot(B) using simple circle_CRV

# creating twk CTRLs
cmds.circle(nr=(0, 0, 1), c=(0, 0, 0), n='ring_CRV')
cmds.group(em=True, name='ring_GRP')
cmds.parent('ring_CRV', 'ring_GRP')

LRTB_name=['L_', 'R_', 'T_', 'B_']
for i in LRTB_name:
    grp = cmds.duplicate('ball_GRP', name='{0}GRP'.format(i), rc=1)[0]
    ctrl = cmds.listRelatives(grp, c=True)[0]
    ctrl = cmds.rename(ctrl, '{0}CTRL'.format(i))

cmds.delete('ring_GRP')

# move the CTRLs to the corresponding joints
cmds.delete(cmds.parentConstraint('L_GRP', L_lip_crn_jnt))
cmds.delete(cmds.parentConstraint('T_GRP', M_lip_crn_jnt))
cmds.delete(cmds.parentConstraint('B_GRP', M_lip_crn_jnt))

# duplicate the R_crn_CTRL from the left one
Right = cmds.duplicate('L_GRP', name='R_GRP', rc=1)[0]
R_ctrl = cmds.listRelatives(Right, c=True)[0]
R_ctrl = cmds.rename(R_ctrl, 'R_CTRL')
# set up R_mouth_offset_GRP
cmds.group(em=True, name='R_mouth_offset_GRP')
cmds.setAttr('R_mouth_offset_GRP.scaleX', -1)
cmds.parent('R_GRP', 'R_mouth_offset_GRP')

###################################################################
# manually move and edit crn_CTRLs, placing/shaping to the desired look
###################################################################
# creating circle_CTRL GRP and DRV for duplicating
cmds.circle(nr=(0, 0, 1), c=(0, 0, 0), n='circle_CRV')
cmds.group(em=True, name='Circle_GRP')
cmds.group(em=True, name='Circle_DRV')
cmds.parent('circle_CRV', 'Circle_DRV')
cmds.parent('Circle_DRV', 'Circle_GRP')

from maya import cmds

def count_CVs(crv):
    crn_cv_count = cmds.ls(crv + ".cv[*]",fl=True)
    crn_n = len(crn_cv_count)
    return crn_n

crn_curves = ["lip_crn_bot_CRV", "lip_crn_top_CRV"]
crn_n = count_CVs(crn_curves[0])

# creating ctrls and jnts that according to the crn_CRVs
for crv in crn_curves:
    cvs = cmds.ls("{0}.cv[*]".format(crv), fl=True)

#creating left side's jnts and ctrls
    for i, cv in enumerate(cvs[:crn_n/2]):
          cvpos = cmds.xform(cv, q=True, t=True, ws=True)
          jnt = cmds.createNode("joint", n="L_{0}_".format(str(i).zfill(2)) + crv.replace("_CRV", "_JNT"))
          jnt_offset = cmds.createNode("joint", n=jnt.replace("_crn", "_offset"))
          cmds.parent(jnt, jnt_offset)
          cmds.xform(jnt_offset, t=cvpos, ws=True)

          grp, drv, ctrl = cmds.duplicate("Circle_GRP", n=jnt.replace("_JNT", "_GRP"), rc=True)
          drv = cmds.rename(drv, jnt.replace("_JNT", "_DRV"))
          ctrl = cmds.rename(ctrl, jnt.replace("_JNT", "_CTRL"))

          cmds.delete(cmds.parentConstraint(jnt, grp))
          cmds.parentConstraint(ctrl, jnt)

#creating right side's jnts and ctrls
    for i, cv in enumerate(cvs[::-1][:(crn_n-1)/2]):
          cvpos = cmds.xform(cv, q=True, t=True, ws=True)
          jnt = cmds.createNode("joint", n="R_{0}_".format(str(i).zfill(2)) + crv.replace("_CRV", "_JNT"))
          jnt_offset = cmds.createNode("joint", n=jnt.replace("_crn", "_offset"))
          cmds.parent(jnt, jnt_offset)
          cmds.xform(jnt_offset, t=cvpos, ws=True)

          grp, drv, ctrl = cmds.duplicate("Circle_GRP", n=jnt.replace("_JNT", "_GRP"), rc=True)
          drv = cmds.rename(drv, jnt.replace("_JNT", "_DRV"))
          ctrl = cmds.rename(ctrl, jnt.replace("_JNT", "_CTRL"))

          cmds.delete(cmds.parentConstraint(jnt, grp))
        #   deleting the R_CTRLs since they won't be needed
          cmds.delete(grp)

#creating middle jnts and ctrls
    cvpos = cmds.xform("{0}.cv[{1}]".format(crv, crn_n/2), q=True, t=True, ws=True)
    jnt = cmds.createNode("joint", n="M_00_" + crv.replace("_CRV", "_JNT"))
    jnt_offset = cmds.createNode("joint", n=jnt.replace("_crn", "_offset"))
    cmds.parent(jnt, jnt_offset)
    cmds.xform(jnt_offset, t=cvpos, ws=True)

    grp, drv, ctrl = cmds.duplicate("Circle_GRP", n=jnt.replace("_JNT", "_GRP"), rc=True)
    drv = cmds.rename(drv, jnt.replace("_JNT", "_DRV"))
    ctrl = cmds.rename(ctrl, jnt.replace("_JNT", "_CTRL"))

    cmds.delete(cmds.parentConstraint(jnt, grp))
    cmds.parentConstraint(ctrl, jnt)

# duplicating L_CTRLs for the right side, group them then placed in R_mouth_offset_GRP
left_CTRLs = cmds.ls('L_*_lip_crn_*_GRP')
cmds.group(em=True, name='L_lip_crn_CTRL_GRP')
cmds.group(em=True, name='R_lip_crn_CTRL_GRP')

cmds.parent(left_CTRLs, 'L_lip_crn_CTRL_GRP')
# duplicating and parenting the left_CTRLs to the joints
for i in left_CTRLs:
    grp, drv, ctrl = cmds.duplicate(i, n=i.replace('L_', 'R_'), rc=1)
    drv = cmds.rename(drv, drv[:-1].replace('L_', 'R_'))
    ctrl = cmds.rename(ctrl, ctrl[:-1].replace('L_', 'R_'))
    cmds.parent(grp, 'R_lip_crn_CTRL_GRP')
    cmds.parentConstraint(ctrl, ctrl.replace('_CTRL', '_JNT'))

cmds.parent('R_lip_crn_CTRL_GRP', 'R_mouth_offset_GRP')
cmds.setAttr('R_lip_crn_CTRL_GRP.rotateY', 0)
cmds.setAttr('R_lip_crn_CTRL_GRP.scaleX', 1)
cmds.setAttr('R_lip_crn_CTRL_GRP.scaleZ', 1)

# parenting the right_CTRLs to the joints 
right_CTRLs = cmds.ls('R_*_lip_crn_*_CTRL')
for i in right_CTRLs:
    cmds.parentConstraint(i, i.replace('_CTRL', '_JNT'))

# tidy up newly created joints
cmds.group(em=True, name='lip_crn_JNT_GRP')
crn_JNTs = cmds.ls('*_*_lip_offset_*_JNT')
cmds.parent(crn_JNTs, 'lip_crn_JNT_GRP')

cmds.delete('Circle_GRP')

###################################################################
# manually move and edit lip_crn_CTRLs, placing/shaping to the desired look
###################################################################
# manually create and place the left and right corner 00_lip_crn_CTRL
###################################################################
# delete history of the crn_CRVs and rebind
# bind the top/bot_crn_JNTs to the top/bot_crn_CRVs
cmds.delete("lip_crn_top_CRV", ch=True)
cmds.delete("lip_crn_bot_CRV", ch=True)

top_crn_JNTs = cmds.ls('*_*_lip_crn_top_JNT')
cmds.skinCluster(top_crn_JNTs, 'lip_crn_top_CRV', dr=4, tsb=1)
bot_crn_JNTs = cmds.ls('*_*_lip_crn_bot_JNT')
cmds.skinCluster(bot_crn_JNTs, 'lip_crn_bot_CRV', dr=4, tsb=1)
###################################################################
# parenting the TBRL_CTRLs to the crn_CTRLs
cmds.parentConstraint('T_CTRL', 'M_00_lip_crn_top_GRP', mo=1)
cmds.parentConstraint('B_CTRL', 'M_00_lip_crn_bot_GRP', mo=1)
cmds.parentConstraint('R_CTRL', 'R_00_lip_crn_GRP', mo=1)
cmds.parentConstraint('L_CTRL', 'L_00_lip_crn_GRP', mo=1)

L_crn_top_GRPs = cmds.ls('L_*_lip_crn_top_GRP')
L_crn_bot_GRPs = cmds.ls('L_*_lip_crn_bot_GRP')
R_crn_top_GRPs = cmds.ls('R_*_lip_crn_top_GRP')
R_crn_bot_GRPs = cmds.ls('R_*_lip_crn_bot_GRP')

for i in L_crn_top_GRPs:
    cmds.parentConstraint('T_CTRL', 'L_CTRL', i, mo=1)
for i in L_crn_bot_GRPs:
    cmds.parentConstraint('B_CTRL', 'L_CTRL', i, mo=1)
for i in R_crn_top_GRPs:
    cmds.parentConstraint('T_CTRL', 'R_CTRL', i, mo=1)
for i in R_crn_bot_GRPs:
    cmds.parentConstraint('B_CTRL', 'R_CTRL', i, mo=1)
###################################################################
# setting the constraint type on the right side to no_flip
R_constraints = cmds.ls('R_*_lip_crn_*_GRP_parentConstraint1')
for i in R_constraints:
    cmds.setAttr('{0}.interpType'.format(i), 0)
###################################################################
# modify the constraints' weights
weights_0 = [0.9, 0.7, 0.2]  # For T/B_local_DRVW0
weights_1 = [0.1, 0.3, 0.8]  # For L/R_local_DRVW1
indices = ["03", "02", "01"]
sides = ["L", "R"]

for side in sides:
    for idx, weight_0, weight_1 in zip(indices, weights_0, weights_1):
        for pos in ["top", "bot"]:
            base_name = "{0}_{1}_lip_crn_{2}_GRP_parentConstraint1".format(side, idx, pos)
            
            weight_0_attr = "T_CTRLW0" if pos == "top" else "B_CTRLW0"
            cmds.setAttr("{0}.{1}".format(base_name, weight_0_attr), weight_0)

            weight_1_attr = "{0}_CTRL1".format(side)
            cmds.setAttr("{0}.{1}".format(base_name, weight_1_attr), weight_1)
###################################################################
# create lips_mst_JNT and CTRL
cmds.createNode("joint", n='lip_mst_JNT')
###################################################################
# manually move it to the inner mouth
###################################################################
# create a simple circle_CTRL as lip_mst_CTRL
cmds.circle(nr=(0, 0, 1), c=(0, 0, 0), n='lip_mst_CTRL')
cmds.group(em=True, name='lip_mst_GRP')
cmds.parent('lip_mst_CTRL', 'lip_mst_GRP')
###################################################################
# manually adjusting the lip_mst_CTRL to desired look
###################################################################
# parent all the CTRLs ubder the lip_mst_CTRL
cmds.parent('lip_crn_JNT_GRP', 'L_lip_crn_CTRL_GRP', 'M_00_lip_crn_top_GRP', 'M_00_lip_crn_bot_GRP',
            'L_GRP', 'B_GRP', 'T_GRP', 'R_mouth_offset_GRP', 'lip_mst_CTRL')
###################################################################
# creating rot_CRVs and start working on the rot set up
# duplicating more CRVs from the 2 initial CRVs
for i in CRVs:
    cmds.duplicate(i, n=i.replace('lip_', 'lip_rot_'))
###################################################################
# manually adjusting the lip_rot_CRVs, sacle flat, narrow, and move back
###################################################################
# creating a groups for lip_CRVs, lip_jaw_CRVs, lip_crn_CRVs, and rot_CRVs
cmds.group(em=True, name='lip_CRV_GRP')
cmds.parent('lip_top_CRV', 'lip_bot_CRV', 'lip_CRV_GRP')
cmds.parent('lip_jaw_top_CRV', 'lip_jaw_bot_CRV', 'lip_CRV_GRP')
cmds.parent('lip_crn_top_CRV', 'lip_crn_bot_CRV', 'lip_CRV_GRP')

cmds.group(em=True, name='lip_rot_CRV_GRP')
cmds.parent('lip_rot_top_CRV', 'lip_rot_bot_CRV', 'lip_rot_CRV_GRP')
rot_CRVs = ['lip_rot_top_CRV', 'lip_rot_bot_CRV']

for i in rot_CRVs:
    cmds.duplicate(i, n=i.replace('lip_', 'lip_jaw_'))

cmds.rebuildCurve('lip_jaw_rot_top_CRV', ch=1, rpo=1, rt=0, end=1, kr=2, kcp=0, kep=1, kt=0, s=6, d=3, tol=0.01)
cmds.rebuildCurve('lip_jaw_rot_bot_CRV', ch=1, rpo=1, rt=0, end=1, kr=2, kcp=0, kep=1, kt=0, s=6, d=3, tol=0.01)

cmds.duplicate('lip_jaw_rot_top_CRV', n='lip_crn_rot_top_CRV')
cmds.duplicate('lip_jaw_rot_bot_CRV', n='lip_crn_rot_bot_CRV')
# bind jaw_top/mid/bot_JNTs to the new jaw_rot_CRVs
cmds.skinCluster(jaw_top_jnt, jaw_mid_jnt, 'lip_jaw_rot_top_CRV', dr=4, tsb=1)
cmds.skinCluster(jaw_mid_jnt, jaw_bot_jnt, 'lip_jaw_rot_bot_CRV', dr=4, tsb=1)

# top_crn_JNTs = cmds.ls('*_*_lip_crn_top_JNT')
cmds.skinCluster(top_crn_JNTs, 'lip_crn_rot_top_CRV', dr=4, tsb=1)
# bot_crn_JNTs = cmds.ls('*_*_lip_crn_bot_JNT')
cmds.skinCluster(bot_crn_JNTs, 'lip_crn_rot_bot_CRV', dr=4, tsb=1)
###################################################################
# parentConstraint the L and R crn_CTRLs #to_be_updated
# 'L_00_lip_crn_CTRL' to 'L_00_lip_crn_top_CTRL' and 'L_00_lip_crn_bot_CTRL'
# 'R_00_lip_crn_CTRL' to 'R_00_lip_crn_top_CTRL' and 'R_00_lip_crn_bot_CTRL'
###################################################################
# exporting the skin weights from jaw_CRVs and import them back to jaw_rot_CRVs #to_be_updated
# exporting the skin weights from crn_CRVs and import them back to crn_rot_CRVs #to_be_updated
# creating BS from crn_CRVs to jaw_CRVs
cmds.blendShape('lip_crn_rot_top_CRV', 'lip_jaw_rot_top_CRV', n='lip_jaw_rot_top_BS', ex='deformPartition\#')
cmds.blendShape('lip_crn_rot_bot_CRV', 'lip_jaw_rot_bot_CRV', n='lip_jaw_rot_bot_BS', ex='deformPartition\#')
cmds.blendShape('lip_jaw_rot_top_BS', edit=True, w=[0, 1])
cmds.blendShape('lip_jaw_rot_bot_BS', edit=True, w=[0, 1])
###################################################################
# create wire deform manually #to_be_updated
###################################################################
# creating twk CTRLs
cmds.circle(nr=(0, 0, 1), c=(0, 0, 0), n='Circle_CRV')
cmds.group(em=True, name='Circle_GRP')
cmds.parent('Circle_CRV', 'Circle_GRP')

n = count_CVs('lip_top_CRV')
###################################################################
# needs to identify sides first
top_cv_list = [cmds.ls('lip_top_CRV' + ".cv[*]",fl=True)]

def get_left_CV(cv_list):
    space_lst = []
    left=1
    for cv in cv_list:
        space = cmds.xform(cv, q=1, t=1, ws=1)
        space_lst.append(space)
    print(space_lst)
    if space_lst[0][0] > space_lst[-1][0]:
        print('space0 is right')
        left=0
        return left
    else:
        print('space0 is left')
        return left
    
left_side = get_left_CV(top_cv_list)
###################################################################
# cv_num = cmds.ls('lip_top_CRV' + ".cv[*]",fl=True)
# n = len(cv_num)

#creating rotation joints and ctrls

mst_JNT = "lip_mst_JNT"
# joints = []
# rot_joints = []
if not left_side:
    for location in ["top", "bot"]:
        offsets = []
        ctrls = []
        upobjs = []
        previous_side = "R"

        for i in range(n-1):
            side = 'M'
            if i<(n-1)/2:
                side = "R"
            elif i>(n-1)/2:
                side = "L"

            jnt = cmds.createNode("joint", n="{0}_{1}_lip_{2}_JNT".format(side, str(i).zfill(2), location))
            rotjnt = cmds.createNode("joint", n="{0}_{1}_lip_rot_{2}_JNT".format(side, str(i).zfill(2), location))
            # joints.append(jnt)
            # rot_joints.append(rotjnt)

            cmds.parent(rotjnt, jnt)
            cmds.parent(jnt, mst_JNT)

            grp, ctrl = cmds.duplicate("Circle_GRP", n=jnt.replace("_JNT", "_twk_GRP"), rc=1)
            ctrl = cmds.rename(ctrl, jnt.replace("_JNT", "_twk_CTRL"))

            pci = cmds.createNode("pointOnCurveInfo", n=ctrl.replace("_CTRL", "_PCI"))
            cmds.connectAttr("lip_{0}_CRVShape.worldSpace[0]".format(location), "{0}.inputCurve".format(pci))
            cmds.connectAttr("{0}.position".format(pci), "{0}.translate".format(grp))
            cmds.setAttr("{0}.parameter".format(pci), i)

            upobj = cmds.spaceLocator(n=grp.replace("_twk_GRP", "_up_obj_LOC"))[0]

            pci = cmds.createNode("pointOnCurveInfo", n=ctrl.replace("_CTRL", "_up_obj_PCI"))
            cmds.connectAttr("lip_rot_{0}_CRVShape.worldSpace[0]".format(location), "{0}.inputCurve".format(pci))
            cmds.connectAttr("{0}.position".format(pci), "{0}.translate".format(upobj))
            cmds.setAttr("{0}.parameter".format(pci), i)

            cmds.pointConstraint(ctrl, jnt, mo=0)

            if i != 0:
                if side == "M":
                        pass
                elif side == "L" and previous_side != "M":
                        cmds.aimConstraint(grp, offsets[-1], mo=0, aimVector=[1, 0, 0], upVector=[0, 0, -1], wut="object",
                                            worldUpObject=upobjs[-1])
                elif side == "R":
                        cmds.aimConstraint(offsets[-1], grp, mo=0, aimVector=[-1, 0, 0], upVector=[0, 0, -1], wut="object",
                                            worldUpObject=upobjs[-1])
            # ctrls.append(ctrl)
            offsets.append(grp)
            upobjs.append(upobj)

            previous_side = side

# delete the Circle_GRP
cmds.delete('Circle_GRP')

# tidy up the scene
upobj_LOC = cmds.ls('*_*_lip_*_up_obj_LOC')
cmds.group(em=True, name='lip_up_obj_LOC_GRP')
cmds.parent(upobj_LOC, 'lip_up_obj_LOC_GRP')
cmds.hide('lip_up_obj_LOC_GRP')

twk_CTRL_GRP = cmds.ls('*_*_lip_*_twk_GRP')
cmds.group(em=True, name='lip_twk_CTRL_GRP')
cmds.parent(twk_CTRL_GRP, 'lip_twk_CTRL_GRP')
###################################################################
# add orientConstraint to the middle twk_CTRL_GRP from the 2 GRPs on each side #to_be_updated
###################################################################
# add orientConstraint from the twk_CTRL_GRP to the lip_rot_JNTs
twk_CTRLs = cmds.ls('*_*_lip_*_twk_CTRL')
for i in twk_CTRLs:
    cmds.orientConstraint(i, i.replace('lip_', 'lip_rot_').replace('_twk_CTRL', '_JNT'))

###################################################################
# manually adjusting the lip_twk_CTRLs to desired look
###################################################################
# Mar 14th major update
# need optimization and adjustments
# instead of creating empty transform nodes, use the existing CTRLs to create the DRVs
# duplicating the original mst_CTRLs group so that the DRVs can inherit the same offset
cmds.duplicate('lip_mst_GRP', n='lip_mst_drv_offset_GRP', rc=1)
# delete the crn_JNT_GRP
cmds.delete('lip_crn_JNT_GRP1')

# deleting the CTRLs' shape and rename
for i in cmds.listRelatives('lip_mst_drv_offset_GRP', ad=1):
    if i.split('_')[-1]=='CTRLShape1':
        cmds.delete(i)
    if i.split('_')[-1]=='parentConstraint2':
        cmds.delete(i)
    if i.split('crn')[-1]=='_top_CTRL1':
        cmds.rename(i, i.replace('_top_CTRL1', '_top_local_DRV'))
    if i.split('crn')[-1]=='_bot_CTRL1':
        cmds.rename(i, i.replace('_bot_CTRL1', '_bot_local_DRV'))
    if i.split('crn')[-1]=='_top_DRV1':
        cmds.rename(i, i.replace('_top_DRV1', '_top_local_SDK_DRV'))
    if i.split('crn')[-1]=='_bot_DRV1':
        cmds.rename(i, i.replace('_bot_DRV1', '_bot_local_SDK_DRV'))
    if i.split('crn')[-1]=='_CTRL1':
        cmds.rename(i, i.replace('CTRL1', 'local_DRV'))
    if i.split('crn')[-1]=='_DRV1':
        cmds.rename(i, i.replace('DRV1', 'local_SDK_DRV'))
    if i.split('_')[-1]=='GRP1':
        cmds.rename(i, i.replace('GRP1', 'local_DRV_GRP'))
    if i.split('_')[-1]=='CTRL1':
        cmds.rename(i, i.replace('_CTRL1', '_local_DRV'))

# connecting the attributes
CTRLs = cmds.ls('*_*_lip_crn_*_CTRL')
for i in CTRLs:
    cmds.connectAttr("{0}.t".format(i), "{0}.t".format(i.replace('_CTRL','_local_DRV')))
    cmds.connectAttr("{0}.r".format(i), "{0}.r".format(i.replace('_CTRL','_local_DRV')))
    cmds.connectAttr("{0}.s".format(i), "{0}.s".format(i.replace('_CTRL','_local_DRV')))
# specify 'top' and 'bot' so it doesn't get confused with the newly created local drivers
DRVs = cmds.ls('*_*_lip_crn_bot_DRV')
for i in DRVs:
    cmds.connectAttr("{0}.t".format(i), "{0}.t".format(i.replace('_DRV','_local_SDK_DRV')))
    cmds.connectAttr("{0}.r".format(i), "{0}.r".format(i.replace('_DRV','_local_SDK_DRV')))
    cmds.connectAttr("{0}.s".format(i), "{0}.s".format(i.replace('_DRV','_local_SDK_DRV')))

DRVs = cmds.ls('*_*_lip_crn_top_DRV')
for i in DRVs:
    cmds.connectAttr("{0}.t".format(i), "{0}.t".format(i.replace('_DRV','_local_SDK_DRV')))
    cmds.connectAttr("{0}.r".format(i), "{0}.r".format(i.replace('_DRV','_local_SDK_DRV')))
    cmds.connectAttr("{0}.s".format(i), "{0}.s".format(i.replace('_DRV','_local_SDK_DRV')))

# connect the LRTB_CTRLs' and lip_mst_CTRL attributes separately
# need optimixation
cmds.connectAttr("{0}.t".format('R_CTRL'), "{0}.t".format('R_local_DRV'))
cmds.connectAttr("{0}.r".format('R_CTRL'), "{0}.r".format('R_local_DRV'))
cmds.connectAttr("{0}.s".format('R_CTRL'), "{0}.s".format('R_local_DRV'))

cmds.connectAttr("{0}.t".format('T_CTRL'), "{0}.t".format('T_local_DRV'))
cmds.connectAttr("{0}.r".format('T_CTRL'), "{0}.r".format('T_local_DRV'))
cmds.connectAttr("{0}.s".format('T_CTRL'), "{0}.s".format('T_local_DRV'))

cmds.connectAttr("{0}.t".format('B_CTRL'), "{0}.t".format('B_local_DRV'))
cmds.connectAttr("{0}.r".format('B_CTRL'), "{0}.r".format('B_local_DRV'))
cmds.connectAttr("{0}.s".format('B_CTRL'), "{0}.s".format('B_local_DRV'))

cmds.connectAttr("{0}.t".format('L_CTRL'), "{0}.t".format('L_local_DRV'))
cmds.connectAttr("{0}.r".format('L_CTRL'), "{0}.r".format('L_local_DRV'))
cmds.connectAttr("{0}.s".format('L_CTRL'), "{0}.s".format('L_local_DRV'))

cmds.connectAttr("{0}.t".format('lip_mst_CTRL'), "{0}.t".format('lip_mst_local_DRV'))
cmds.connectAttr("{0}.r".format('lip_mst_CTRL'), "{0}.r".format('lip_mst_local_DRV'))
cmds.connectAttr("{0}.s".format('lip_mst_CTRL'), "{0}.s".format('lip_mst_local_DRV'))
####################################################################
# delete the constrainsts on the crn_JNTs
crn_JNT_PC = cmds.ls('*_*_lip_crn_*_JNT_parentConstraint1')
cmds.delete(i for i in crn_JNT_PC)

# re-constraint the joints with the local_DRV
local_DRV = cmds.ls('*_*_lip_crn_*_local_DRV')
for i in local_DRV:
    cmds.parentConstraint(i, i.replace('_local_DRV', '_JNT'), mo=1)

# re-constraint the TBRL_CTRLs to the crn_CTRLs on the new local_DRVs
# parenting the TBRL_CTRLs to the crn_CTRLs
cmds.parentConstraint('T_local_DRV', 'M_00_lip_crn_top_local_DRV_GRP', mo=1)
cmds.parentConstraint('B_local_DRV', 'M_00_lip_crn_bot_local_DRV_GRP', mo=1)
cmds.parentConstraint('R_local_DRV', 'R_00_lip_crn_local_DRV_GRP', mo=1)
cmds.parentConstraint('L_local_DRV', 'L_00_lip_crn_local_DRV_GRP', mo=1)

L_crn_top_local_DRV_GRPs = cmds.ls('L_*_lip_crn_top_local_DRV_GRP')
L_crn_bot_local_DRV_GRPs = cmds.ls('L_*_lip_crn_bot_local_DRV_GRP')
R_crn_top_local_DRV_GRPs = cmds.ls('R_*_lip_crn_top_local_DRV_GRP')
R_crn_bot_local_DRV_GRPs = cmds.ls('R_*_lip_crn_bot_local_DRV_GRP')

for i in L_crn_top_local_DRV_GRPs:
    cmds.parentConstraint('T_local_DRV', 'L_local_DRV', i, mo=1)
for i in L_crn_bot_local_DRV_GRPs:
    cmds.parentConstraint('B_local_DRV', 'L_local_DRV', i, mo=1)
for i in R_crn_top_local_DRV_GRPs:
    cmds.parentConstraint('T_local_DRV', 'R_local_DRV', i, mo=1)
for i in R_crn_bot_local_DRV_GRPs:
    cmds.parentConstraint('B_local_DRV', 'R_local_DRV', i, mo=1)
###################################################################
# modify the constraints' weights
# should be the same as above weight values

# weights_0 = [0.9, 0.7, 0.2]  # For T/B_local_DRVW0
# weights_1 = [0.1, 0.3, 0.8]  # For L/R_local_DRVW1
# indices = ["03", "02", "01"]
# sides = ["L", "R"]

for side in sides:
    for idx, weight_0, weight_1 in zip(indices, weights_0, weights_1):
        for pos in ["top", "bot"]:
            base_name = "{0}_{1}_lip_crn_{2}_local_DRV_GRP_parentConstraint1".format(side, idx, pos)
            
            weight_0_attr = "T_local_DRVW0" if pos == "top" else "B_local_DRVW0"
            cmds.setAttr("{0}.{1}".format(base_name, weight_0_attr), weight_0)

            weight_1_attr = "{0}_local_DRVW1".format(side)
            cmds.setAttr("{0}.{1}".format(base_name, weight_1_attr), weight_1)
###################################################################
# parentConstraint the L and R local_DRVs #to_be_updated
# 'L_00_lip_crn_local_DRV' to 'L_00_lip_crn_top_local_DRV' and 'L_00_lip_crn_bot_local_DRV'
# 'R_00_lip_crn_local_DRV' to 'R_00_lip_crn_top_local_DRV' and 'R_00_lip_crn_bot_local_DRV'
###################################################################
# create offset_GRP/DRV for jaw and parent them
cmds.group(em=1, n='jaw_offset_top_GRP')
cmds.group(em=1, n='jaw_offset_top_DRV')
cmds.group(em=1, n='jaw_offset_bot_GRP')
cmds.group(em=1, n='jaw_offset_bot_DRV')

cmds.parent('jaw_offset_top_DRV', 'jaw_offset_top_GRP')
cmds.parent('jaw_offset_bot_DRV', 'jaw_offset_bot_GRP')

# position the jaw_offset_GRPs to top_jaw_0_JNT
cmds.delete(cmds.parentConstraint('face_bot_JNT', 'jaw_offset_top_GRP', mo=0))
cmds.delete(cmds.parentConstraint('face_bot_JNT', 'jaw_offset_bot_GRP', mo=0))

# connect the translate and rotate from top_jaw_0_JNT to jaw_offset_top_DRV and jaw_JNT to jaw_offset_bot_DRV
cmds.connectAttr('top_jaw_0_JNT.translate', 'jaw_offset_top_DRV.translate')
cmds.connectAttr('top_jaw_0_JNT.rotate', 'jaw_offset_top_DRV.rotate')
cmds.connectAttr('jaw_JNT.translate', 'jaw_offset_bot_DRV.translate')
cmds.connectAttr('jaw_JNT.rotate', 'jaw_offset_bot_DRV.rotate')

# parent the offset_GRPs to jaw_mst_CTRL
cmds.parent('jaw_offset_top_GRP', 'lip_mst_CTRL')
cmds.parent('jaw_offset_bot_GRP', 'lip_mst_CTRL')

# constraint the jaw_offset_DRVs to the LRTB_GRP
cmds.parentConstraint('jaw_offset_bot_DRV', 'B_GRP', mo=1)
cmds.parentConstraint('jaw_offset_top_DRV', 'jaw_offset_bot_DRV', 'R_GRP', mo=1)
cmds.parentConstraint('jaw_offset_top_DRV', 'jaw_offset_bot_DRV', 'L_GRP', mo=1)

# parent the lip_mst_JNT to face_bot_JNT
cmds.parent('lip_mst_JNT', 'face_bot_JNT')

# parent the lip_mst_JNT to lip_mst_JNT
cmds.parent('lip_mst_JNT', 'lip_mst_JNT')

####################################################################
# setting up lip joints' labels for weight painting mirror
R_lip = cmds.ls('R_*_lip_*_JNT')
for i in R_lip:
    cmds.setAttr('{0}.side'.format(i), 2)
    cmds.setAttr('{0}.type'.format(i), 18)
    n=int(i.split('_')[1])
    p=i.split('_')[-2]
    cmds.setAttr('{0}.otherType'.format(i), 'lip_{0}_{1}'.format(abs(n-14), p), type='string')

R_rot_lip = cmds.ls('R_*_lip_rot_*_JNT')
for i in R_rot_lip:
    cmds.setAttr('{0}.side'.format(i), 2)
    cmds.setAttr('{0}.type'.format(i), 18)
    n=int(i.split('_')[1])
    p=i.split('_')[-2]
    cmds.setAttr('{0}.otherType'.format(i), 'lip_{0}_rot_{1}'.format(abs(n-14), p), type='string')

L_lip = cmds.ls('L_*_lip_*_JNT')
for i in L_lip:
    cmds.setAttr('{0}.side'.format(i), 1)
    cmds.setAttr('{0}.type'.format(i), 18)
    n=i.split('_')[1]
    p=i.split('_')[-2]
    cmds.setAttr('{0}.otherType'.format(i), 'lip_{0}_{1}'.format(n[1:], p), type='string')

L_rot_lip = cmds.ls('L_*_lip_rot_*_JNT')
for i in L_rot_lip:
    cmds.setAttr('{0}.side'.format(i), 1)
    cmds.setAttr('{0}.type'.format(i), 18)
    n=i.split('_')[1]
    p=i.split('_')[-2]
    cmds.setAttr('{0}.otherType'.format(i), 'lip_{0}_rot_{1}'.format(n[1:], p), type='string')
