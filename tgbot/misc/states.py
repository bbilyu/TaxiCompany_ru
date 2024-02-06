from aiogram.fsm.state import StatesGroup, State



class AddCar(StatesGroup):
    FacialPhoto = State()
    Brand = State()
    Model = State()
    ReleaseYear = State()
    StateNumber = State()
    Cost = State()



class AddDriver(StatesGroup):
    FacialPhoto = State()
    Surname = State()
    Name = State()
    Patronymic = State()
    Birthdate = State()
    DateOfStartWork = State()
    DateOfTermination = State()
    ContactInformation = State()
    AdditionalInformation = State()

class AddCompensationForDamages(StatesGroup):
    CarId = State()
    DriverId = State()
    Date = State()
    Description = State()
    Amount = State()
    PayersId = State()

class AddPerformer(StatesGroup):
    PerformerName = State()


class AddServiceHistory(StatesGroup):
    CarId = State()
    DriverId = State()
    Date = State()
    ServiceType = State()
    Amount = State()
    PerformerId = State()

class AddRecoveryFromDamages(StatesGroup):
    CarId = State()
    DriverId = State()
    Date = State()
    Description = State()
    Amount = State()
    PayersId = State()

class AddOtherExpenses(StatesGroup):
    CarId = State()
    DriverId = State()
    Date = State()
    Description = State()
    Amount = State()
    PerformerId = State()

class AddRange(StatesGroup):
    StartDate = State()
    EndDate = State()
class AddProfitRange(StatesGroup):
    StartDate = State()

class AddRentPayment(StatesGroup):
    CarId = State()
    DriverId = State()
    Date = State()
    Сomment = State()
    Amount = State()
    DriverRent = State()

class AddMedia(StatesGroup):
    Inspections = State()
    Media = State()
    MediaServiceHistory = State()
    MediaCompensationForDamages = State()
    MediaRecoveryFromDamages = State()
    MediaOtherExpenses = State()

class AddManagement(StatesGroup):
    DriverRent = State()

class UpdateDriverInManagement(StatesGroup):
    DriverRent = State()

class UpdateDriver(StatesGroup):
    FacialPhoto = State()
    Surname = State()
    Name = State()
    Patronymic = State()
    Birthdate = State()
    DateOfStartWork = State()
    DateOfTermination = State()
    ContactInformation = State()
    AdditionalInformation = State()

class UpdateCar(StatesGroup):
    FacialPhoto = State()
    Brand = State()
    Model = State()
    ReleaseYear = State()
    StateNumber = State()
    Cost = State()

class UpdateServiceHistory(StatesGroup):
    Media = State()
    CarId = State()
    DriverId = State()
    Date = State()
    ServiceType = State()
    Amount = State()
    PerformerId = State()

class UpdateCompensationForDamages(StatesGroup):
    Media = State()
    CarId = State()
    DriverId = State()
    Date = State()
    Description = State()
    Amount = State()
    PayersId = State()

class UpdateRentPayment(StatesGroup):
    Date = State()
    Comment = State()
    Amount = State()

class UpdateRecoveryFromDamages(StatesGroup):
    Media = State()
    CarId = State()
    DriverId = State()
    Date = State()
    Description = State()
    Amount = State()
    PayersId = State()

class UpdateOtherExpenses(StatesGroup):
    Media = State()
    CarId = State()
    DriverId = State()
    Date = State()
    Description = State()
    Amount = State()
    PayersId = State()