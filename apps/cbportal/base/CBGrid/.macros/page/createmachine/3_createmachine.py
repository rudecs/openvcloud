from JumpScale.portal.docgenerator.popup import Popup

def main(j, args, params, tags, tasklet):
    actors = j.apps.cloudbroker.iaas.cb.extensions.imp.actors.cloudapi
    params.result = page = args.page
    cloudspaceId = args.getTag('cloudspaceId')

    popup = Popup(id='createmachine', header='Create Machine', submit_url='/restmachine/cloudbroker/machine/create')
    popup.addText('Machine Name', 'name', required=True)
    popup.addText('Machine Description', 'description', required=True)
    sizes = actors.sizes.list()
    images = actors.images.list()
    dropsizes = list()
    dropdisksizes = list()
    dropimages = list()
    def sizeSorter(size):
        return size['memory']

    def imageSorter(image):
        return image['type'] + image['name']

    for image in sorted(images, key=imageSorter):
        dropimages.append(("%(type)s: %(name)s" % image, image['id']))

    for size in sorted(sizes, key=sizeSorter):
        dropsizes.append(("%(memory)s MB" % size, size['id']))

    for size in (10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100):
        dropdisksizes.append(("%s GB" % size, str(size)))

    popup.addDropdown('Choose Image', 'imageId', dropimages)
    popup.addDropdown('Choose Memory', 'sizeId', dropsizes)
    popup.addDropdown('Choose Disk Size', 'disksize', dropdisksizes)

    popup.addHiddenField('cloudspaceId', cloudspaceId)

    popup.write_html(page)

    return params


def match(j, args, params, tags, tasklet):
    return True
