_tab_registry = {}


def register_tab(tab_name):
    """装饰器：注册Tab类
    
    用法：
    @register_tab("图片下载")
    class ImageDownloadTab(BaseTab):
        pass
    """

    def decorator(tab_class):
        _tab_registry[tab_name] = tab_class
        return tab_class

    return decorator


def get_tab(tab_name):
    """根据名称获取Tab类"""
    return _tab_registry.get(tab_name)


def get_all_tabs():
    """获取所有已注册的Tab（名称到类的映射）"""
    return _tab_registry.copy()


def create_tab(tab_name):
    """根据名称创建Tab实例"""
    tab_class = get_tab(tab_name)
    if tab_class:
        return tab_class()
    return None


def get_tab_names():
    """获取所有已注册的Tab名称（按注册顺序）"""
    return list(_tab_registry.keys())
