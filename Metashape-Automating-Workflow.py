
'''
Metashape 1.6.3.

For matching accuracy the correspondence:
Highest = 0
High = 1
Medium = 2
Low = 4
Lowest = 8

For depth maps quality:
Ultra = 1
High = 2
Medium = 4
Low = 8
Lowest = 16
'''

import Metashape
from math import sqrt

def FixGCP():
	print("--------- Start Script FixGCPs--------")
	app = Metashape.Application()
	chunk = Metashape.app.document.chunk
	
	pane = Metashape.app.PhotosPane()

	error_sum = 0
	pic_error = []
	chunk.sortMarkers()
	print( '============ Error of Markers ===========')
	limit = app.getFloat(label='input your value error(pixel) to not accept', value=0.3)


	for marker in chunk.markers:    
		accept = True
		error_sum = (0, 0)

		print( '---> Marker name : {:>8} '.format( marker.label)) 
		for camera in marker.projections.keys(): 
			proj = marker.projections[camera].coord 	
			reproj = camera.project(marker.position)
			error = (proj - reproj).norm()
			error_sum = ( error_sum[0] + error**2, error_sum[1] + 1 )
			print('photo {} | error {:.3f} pix'.format(camera.label,error))
			if error > limit :
				pic_error.append(camera)
				accept = False
				
		error_pix =  sqrt(error_sum[0] / error_sum [1] )
		print( '{:>15} error : {:.3f} pix '.format( 'Total', error_pix),'\n' )
		
		if accept == False :
			app.messageBox("Not Acceopt !!,  GCP : {} --> Error > {} pixel ".format(marker.label,limit))
			print('Error > {} pixel in Marker: {}'.format(limit, marker.label) )
			marker.selected = True
			pane.setFilter(marker)
			pane.setFilter(pic_error)
			break
		
		else:
			marker.selected = False
			pic_error = []
			
	if accept == True :
		app.messageBox("Accepted ! , All GCPs error < {} pixel".format(limit))
		print( ' All GCP... error < {} pixel'.format(limit) )
	print("Click 'BuilAll' at toolbar to continue..")
	print("----------------- End of Script --------------")



def checkProj(chunk):
	point_cloud = chunk.point_cloud
	points = point_cloud.points
	npoints = len(points)

	projections = chunk.point_cloud.projections 
	print('# checking.... pts/photo')
	

	for camera in chunk.cameras:

		point_index = 0
		photo_num = 0
		ns = 0
		for proj in projections[camera]:
			track_id = proj.track_id
			while point_index < npoints and points[point_index].track_id < track_id:
				point_index += 1
			if point_index < npoints and points[point_index].track_id == track_id:
				if not points[point_index].valid :
					continue
				photo_num += 1
				if points[point_index].selected :
					ns += 1

		if photo_num- ns < 100:
			print('pic {} |  Projections : {} --> after selected : {}'.format (\
				camera.label, photo_num, photo_num- ns) )
			print('!!! projection < 100 points ')
			return False

	return True


def ReconstUncertainly( chunk ):
	point_cloud = chunk.point_cloud
	npoints = len(point_cloud.points)

	print( '\n', '......Start ReconstructionUncertainty.....' )

	fltr = Metashape.PointCloud.Filter()
	fltr.init(chunk, Metashape.PointCloud.Filter.ReconstructionUncertainty)
	values = fltr.values.copy()
	values.sort()
	level = values[-1]
	print( '--> level start : ', level)

	if level < 10 :
		print( '--> level less than 10 --> set level = 10' )
		level = 10
	else :
		print( '--> level more than 10 --> set level = 15' )
		level = 15
		
	flag = 0
	print('flag = 0')

	i=0
	while True:
		i+=1
		print('================== loop {} ==================='.format(i))

		fltr = Metashape.PointCloud.Filter()
		fltr.init(chunk, Metashape.PointCloud.Filter.ReconstructionUncertainty)
			
		print( 'Reconstruction Uncertainly with level =', level)
		fltr.selectPoints(level)
		nselected = len([p for p in point_cloud.points if p.selected])


		print( 'num point at 50% : {} | selected points : {}'.format(npoints/2, nselected))
		if nselected > npoints/2 :
			print('--> pts > 50% --> Resetting Selection.. ')
			fltr.resetSelection()

			values = fltr.values.copy()
			values.sort()
			level = values[ int(len(values) * 0.5)]
			print( 'set points at 50% --> level = {}'.format(level) )
			
			fltr.selectPoints(level)
			nselected = len([p for p in point_cloud.points if p.selected])
			flag = 1
			print('flag = 1 ')
			
		print( 'selected points < 50 %... pass' )
		print('--> set level = {} | {} selected points'.format(level, nselected))
		

		CheckProj_bool = checkProj(chunk)
		if CheckProj_bool == False:
				print('--> check pts/photo > 100 points... unpass !')
				
				print('# Resetting... Selection... ')
				fltr.resetSelection()

				print('Reconstruction Uncertainly Stop.. ')
				break

			
		print('--> check pts/photo > 100 points... pass')
		print('--> level : {:.5f}  |  all points :{}   |  --> selected pnts: {}'.format\
										( level, len(point_cloud.points), nselected ))
		print( '# removing... selected points' )
		point_cloud.removeSelectedPoints()
		print('--> delete {} points ... done '.format(nselected))

		chunk.optimizeCameras(fit_f=True, fit_cx=True, fit_cy=True, fit_k1=True, \
								  fit_k2=True, fit_k3=True, fit_p1=True, fit_p2=True,)

		if flag == 1:
			print('flag = 1 --> Reconstruction Uncertainly Stop..')
			break
		
		else:
			if level == 10 :
				print( 'level == 10 --> Reconstruction Uncertainly End..' )
				break
			if nselected == 0 :
				print( 'seliected points == 0 --> End..' )
				break
			else:
				print( 'decrease level = 2.5 ')
				level -= 2.5
				continue

def ProjectionAccuracy( chunk ):
	point_cloud = chunk.point_cloud
	npoints = len(point_cloud.points)

	print( '\n', '================== Start ProjectionAccuracy ==================' )

	fltr = Metashape.PointCloud.Filter()
	fltr.init(chunk, Metashape.PointCloud.Filter.ProjectionAccuracy)
	values = fltr.values.copy()
	values.sort()
	level = values[-1]
	print( '--> level start : ', level)


	print( 'set level = 3' )
	level = 3
		
	flag = 0
	print('flag = 0')

	i=0
	while True:
		i+=1
		print('================== loop {} ==================='.format(i))

		fltr = Metashape.PointCloud.Filter()
		fltr.init(chunk, Metashape.PointCloud.Filter.ProjectionAccuracy)
			
		print( 'Projection Accuracy with level =', level)
		fltr.selectPoints(level)
		nselected = len([p for p in point_cloud.points if p.selected])


		print( 'num point at 50% : {} | selected points : {}'.format(npoints/2, nselected))
		if nselected > npoints/2 :
			print('--> pts > 50% --> Resetting... Selection.. ')
			fltr.resetSelection()

			values = fltr.values.copy()
			values.sort()
			level = values[ int(len(values) * 0.5)]
			print( 'set points at 50% --> level = {}'.format(level) )
			
			fltr.selectPoints(level)
			nselected = len([p for p in point_cloud.points if p.selected])
			flag = 1
			print('flag = 1 ')
			
		print( 'selected points < 50 %... pass' )
		print('--> set level = {} | {} selected points'.format(level, nselected))
		

		CheckProj_bool = checkProj(chunk)
		if CheckProj_bool == False:
				print('--> check pts/photo > 100 points... unpass !')
				
				print('# Resetting... Selection... ')
				fltr.resetSelection()

				print('Projection Accuracy Stop.. ')
				break

			
		print('--> check pts/photo > 100 points... pass')
		print('--> level : {:.5f}  |  all points :{}   |  --> selected pnts: {}'.format\
										( level, len(point_cloud.points), nselected ))
		print( '# removing... selected points' )
		point_cloud.removeSelectedPoints()
		print('--> delete {} points ... done '.format(nselected))

		chunk.optimizeCameras(fit_f=True, fit_cx=True, fit_cy=True, fit_k1=True, \
								  fit_k2=True, fit_k3=True, fit_p1=True, fit_p2=True,)

		if flag == 1:
			print('flag = 1 --> Projection Accuracy Stop..')
			break
		
		else:
			if level == 2 :
				print( 'level == 2 --> Projection Accuracy End..' )
				break

			if nselected == 0 :
				print( 'seliected points == 0 --> End..' )
				break
			else:
				print( 'decrease level = 0.1 ')
				level -= 0.1
				continue


def ReprojectionError( chunk ):
	point_cloud = chunk.point_cloud
	npoints = len(point_cloud.points)

	print( '\n', '================== Start ReprojectionError ==================' )

	fltr = Metashape.PointCloud.Filter()
	fltr.init(chunk, Metashape.PointCloud.Filter.ReprojectionError)
	values = fltr.values.copy()
	values.sort()
	level = values[-1]
	print( '--> level start : ', level)

	print( 'set level = 0.3' )
	level = 0.3
		
	flag = 0
	print('flag = 0')

	i=0
	while True:
		i+=1
		print('================== loop {} ==================='.format(i))

		fltr = Metashape.PointCloud.Filter()
		fltr.init(chunk, Metashape.PointCloud.Filter.ReprojectionError)
			
		print( 'Reprojection Error with level =', level)
		fltr.selectPoints(level)
		nselected = len([p for p in point_cloud.points if p.selected])


		print( 'num point at 10% : {} | selected points : {}'.format(npoints/2, nselected))
		if nselected > npoints*0.1 :
			print('--> pts > 10% --> Resetting... Selection.. ')
			fltr.resetSelection()

			values = fltr.values.copy()
			values.sort()
			level = values[ int(len(values) * 0.1)]
			print( '--> set points = 10% --> level = {}'.format(level) )
			
			fltr.selectPoints(level)
			nselected = len([p for p in point_cloud.points if p.selected])
			print('{} selected '.format(nselected))
			flag = 1
			print('flag = 1 ')
			
		print( 'selected points < 10 %... pass' )
		print('--> set level = {} | {} selected points'.format(level, nselected))
		

		CheckProj_bool = checkProj(chunk)
		if CheckProj_bool == False:
				print('--> check pts/photo > 100 points... unpass !')
				
				print('# Resetting... Selection... ')
				fltr.resetSelection()

				print('Reprojection Error Stop.. ')
				break

			
		print('--> check pts/photo > 100 points... pass')
		print('--> level : {:.5f}  |  all points :{}   |  --> selected pnts: {}'.format\
										( level, len(point_cloud.points), nselected ))
		print( '# removing... selected points' )
		point_cloud.removeSelectedPoints()
		print('--> delete {} points ... done '.format(nselected))

		chunk.optimizeCameras(fit_f=True, fit_cx=True, fit_cy=True, fit_k1=True, \
								  fit_k2=True, fit_k3=True, fit_p1=True, fit_p2=True,)

		if flag == 1:
			print('flag = 1 --> Reprojection Error Stop..')
			break
		
		else:
			if level == 0.3 :
				print( 'level == 0.3 --> End..' )
				break
			if nselected == 0 :
				print( 'seliected points == 0 --> End..' )

def convertCRS(chunk, out_crs):
	chunk.updateTransform()

	for camera in chunk.cameras:
		if camera.reference.location:
			camera.reference.location = Metashape.CoordinateSystem.transform(camera.reference.location, chunk.crs, out_crs)
	
	chunk.crs = out_crs
	chunk.updateTransform()
	



def align( chunk ):
	chunk.matchPhotos(downscale=2, generic_preselection=True, reference_preselection=False)
	chunk.alignCameras()


def optimize_loop( chunk ):

	for i in range(2):
		
		chunk.optimizeCameras(  fit_f=True,     fit_cx=True,    fit_cy=True,    fit_b1=False,    fit_b2=False,    fit_k1=True,\
								fit_k2=True,    fit_k3=True,    fit_k4=False,   fit_p1=True,    fit_p2=True,    fit_p3=False,\
								fit_p4=False)


def Build():
	doc = Metashape.app.document
	chunk = doc.chunk
	doc.chunk = chunk
	doc.save()

	if chunk.dense_cloud is None:
		chunk.buildDepthMaps(downscale=4, filter_mode=Metashape.AggressiveFiltering)
		chunk.buildDenseCloud()
		doc.save()

	if chunk.model is None:
		chunk.buildModel(surface_type=Metashape.Arbitrary, interpolation=Metashape.EnabledInterpolation)
		doc.save()

	if chunk.elevation is None:
		chunk.buildUV(mapping_mode=Metashape.GenericMapping)
		chunk.buildTexture(blending_mode=Metashape.MosaicBlending, texture_size=4096)

		doc.save()
		chunk = doc.chunk
		chunk.buildDem(source_data=Metashape.DenseCloudData, interpolation=Metashape.EnabledInterpolation)
			
		doc.save()
	if chunk.orthomosaic is None:
		chunk.buildOrthomosaic(surface_data=Metashape.ElevationData, blending_mode=Metashape.MosaicBlending)

	doc.save()


if __name__ == '__main__':


	app = Metashape.Application()
	doc = Metashape.app.document
	
	project_path = Metashape.app.getSaveFileName()
	if project_path[-4:].lower() != ".psx":
		project_path += ".psx"
	doc.save(project_path)

	chunk_list = doc.chunks
	for chunk in chunk_list:
		doc.chunk = chunk

		out_crs = Metashape.app.getCoordinateSystem( 'choose CRS like your GCP', chunk.crs )
		convertCRS(chunk, out_crs)

		GCP = Metashape.app.getBool(label='If yot have GCP select "yes", program will BREAK to give you import GCP after align photo done. Select "No" program will run buil all finish.')

		if chunk.point_cloud is None:
			align( chunk )
			optimize_loop( chunk )
			ReconstUncertainly( chunk )
			ProjectionAccuracy( chunk )


		if not GCP :
			pass

		else :
			Metashape.app.addMenuItem("CheckGCP", FixGCP)
			Metashape.app.addMenuItem("BuildAll", Build)
			Metashape.app.messageBox('Fix your GCP by use "CheckGCP" on toolbar until message show "Accepted", then click "BuilAll" on toolbar.')
			break

		ReprojectionError( chunk )
		Build()
 

		
	
	
